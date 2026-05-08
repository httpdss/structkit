import argparse
import json
import os

import yaml
from jinja2 import Environment

from structkit.commands import Command
from structkit.completers import file_strategy_completer, structures_completer
from structkit.filters import (
  env as env_get,
  from_json,
  from_yaml,
  gen_uuid,
  get_default_branch,
  get_latest_release,
  now_iso,
  read_file,
  slugify,
  to_json,
  to_yaml,
)
from structkit.utils import get_current_repo


class ExplainCommand(Command):
  """Preview how a structure resolves without creating files or running hooks."""

  REMOTE_PREFIXES = (
    "https://",
    "github://",
    "githubhttps://",
    "githubssh://",
    "s3://",
    "gs://",
  )

  def __init__(self, parser):
    super().__init__(parser)
    parser.description = "Explain structure resolution without writing files or running hooks"
    structure_arg = parser.add_argument(
      'structure_definition',
      nargs='?',
      default='.struct.yaml',
      type=str,
      help='Built-in structure name or path to a YAML structure file (default: .struct.yaml)'
    )
    structure_arg.completer = structures_completer
    parser.add_argument('base_path', nargs='?', default='.', type=str, help='Base path used to resolve generated paths (default: current directory)')
    parser.add_argument(
      '-s',
      '--structures-path',
      type=str,
      help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
      default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
    )
    parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('--json', action='store_true', dest='json_output', help='Output the explanation as JSON')
    parser.add_argument('-o', '--output', choices=['text', 'json'], default='text', help='Output format (default: text)')
    parser.add_argument(
      '-f',
      '--file-strategy',
      type=str,
      choices=['overwrite', 'skip', 'append', 'rename', 'backup'],
      default=os.getenv('STRUCTKIT_FILE_STRATEGY', 'overwrite'),
      help='File conflict strategy to explain (env: STRUCTKIT_FILE_STRATEGY)'
    ).completer = file_strategy_completer
    parser.add_argument('--mappings-file', type=str, action='append', help='Path to a YAML mappings file (can be specified multiple times)')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    mappings = self._load_mappings(getattr(args, 'mappings_file', None))
    explanation = self.explain(args, mappings=mappings)
    if explanation is None:
      return

    if args.json_output or args.output == 'json':
      print(json.dumps(explanation, indent=2, sort_keys=True))
    else:
      print(self._format_text(explanation))

  def explain(self, args, mappings=None):
    if isinstance(args, dict):
      args = argparse.Namespace(**args)

    vars_provided = self._parse_template_vars(getattr(args, 'vars', None))
    explanation = {
      "structure_definition": args.structure_definition,
      "base_path": args.base_path,
      "file_strategy": getattr(args, 'file_strategy', 'overwrite'),
      "variables": [],
      "files": [],
      "folders": [],
      "remote_files": [],
      "hooks": {"pre": [], "post": []},
      "notes": ["No files or folders are created and hooks are not executed by explain."],
    }
    self._collect_structure(
      args.structure_definition,
      args.base_path,
      getattr(args, 'structures_path', None),
      vars_provided,
      mappings or {},
      explanation,
      depth=0,
      parent_chain=[],
      file_strategy=getattr(args, 'file_strategy', 'overwrite'),
    )
    return explanation

  def _collect_structure(self, structure_definition, base_path, structures_path, template_vars, mappings, explanation, depth, parent_chain, file_strategy):
    resolved = self._resolve_structure_path(structure_definition, structures_path)
    if resolved in parent_chain:
      explanation["notes"].append(f"Skipped recursive structure reference: {structure_definition}")
      return

    config = self._load_yaml_config(structure_definition, structures_path)
    if config is None:
      return

    config_variables = config.get('variables', []) or []
    resolved_vars = self._resolve_variables(config_variables, template_vars)
    for variable in resolved_vars:
      variable["structure"] = structure_definition
      variable["depth"] = depth
      explanation["variables"].append(variable)

    render_context = {**{v["name"]: v.get("value") for v in resolved_vars}, **template_vars}
    if mappings:
      render_context['mappings'] = mappings

    for hook in config.get('pre_hooks', []) or []:
      explanation["hooks"]["pre"].append({"command": self._render(str(hook), render_context), "structure": structure_definition, "depth": depth})
    for hook in config.get('post_hooks', []) or []:
      explanation["hooks"]["post"].append({"command": self._render(str(hook), render_context), "structure": structure_definition, "depth": depth})

    for item in config.get('files', config.get('structure', [])) or []:
      if not isinstance(item, dict):
        continue
      for name, content in item.items():
        rendered_name = self._render(str(name), render_context)
        file_path = os.path.join(base_path, rendered_name)
        exists = os.path.exists(file_path)
        entry = {
          "path": file_path,
          "name": rendered_name,
          "structure": structure_definition,
          "depth": depth,
          "exists": exists,
          "conflict_behavior": self._conflict_behavior(exists, content, file_strategy),
          "source": "inline",
        }
        if isinstance(content, dict):
          if content.get('file'):
            remote = self._render(str(content.get('file')), render_context)
            entry["source"] = "remote" if self._is_remote(remote) else "local_file"
            entry["content_location"] = remote
            if self._is_remote(remote):
              explanation["remote_files"].append({"path": file_path, "content_location": remote, "structure": structure_definition, "depth": depth})
          if content.get('skip'):
            entry["skip"] = True
          if content.get('skip_if_exists'):
            entry["skip_if_exists"] = True
          if content.get('user_prompt'):
            entry["source"] = "prompt"
            entry["prompt"] = "Content would be generated from user_prompt during generate."
        explanation["files"].append(entry)

    for item in config.get('folders', []) or []:
      if not isinstance(item, dict):
        continue
      for folder, content in item.items():
        rendered_folder = self._render(str(folder), render_context)
        folder_path = os.path.join(base_path, rendered_folder)
        content = content or {}
        structs = content.get('struct') if isinstance(content, dict) else None
        structs_list = structs if isinstance(structs, list) else ([structs] if isinstance(structs, str) else [])
        with_vars = self._render_with_vars(content.get('with', {}) if isinstance(content, dict) else {}, render_context, mappings)
        explanation["folders"].append({
          "path": folder_path,
          "name": rendered_folder,
          "structure": structure_definition,
          "depth": depth,
          "exists": os.path.exists(folder_path),
          "structs": structs_list,
          "with": with_vars,
        })
        for nested in structs_list:
          nested_vars = {**template_vars, **with_vars}
          self._collect_structure(nested, folder_path, structures_path, nested_vars, mappings, explanation, depth + 1, parent_chain + [resolved], file_strategy)

  def _resolve_structure_path(self, structure_definition, structures_path):
    normalized = structure_definition[7:] if structure_definition.startswith("file://") else structure_definition
    if normalized.endswith(('.yaml', '.yml')):
      return os.path.abspath(normalized)

    search_roots = []
    if structures_path:
      search_roots.append(structures_path)
    this_file = os.path.dirname(os.path.realpath(__file__))
    search_roots.append(os.path.join(this_file, "..", "contribs"))
    for root in search_roots:
      for suffix in ("", ".yaml", ".yml"):
        candidate = os.path.join(root, f"{normalized}{suffix}")
        if os.path.exists(candidate):
          return os.path.abspath(candidate)
    return os.path.abspath(normalized)

  def _load_yaml_config(self, structure_definition, structures_path):
    file_path = self._resolve_structure_path(structure_definition, structures_path)
    if not os.path.exists(file_path):
      self.logger.error(f"❗ File not found: {file_path}")
      return None
    with open(file_path, 'r') as f:
      return yaml.safe_load(f) or {}

  def _parse_template_vars(self, vars_str):
    result = {}
    if not vars_str:
      return result
    tokens = [t.strip() for t in vars_str.strip(', ').split(',')]
    for token in tokens:
      if not token or '=' not in token:
        continue
      key, value = token.split('=', 1)
      key = key.strip()
      if key:
        result[key] = value
    return result

  def _resolve_variables(self, config_variables, template_vars):
    resolved = []
    seen = set()
    for item in config_variables:
      if not isinstance(item, dict):
        continue
      for name, definition in item.items():
        definition = definition or {}
        value = template_vars.get(name, definition.get('default'))
        env_key = definition.get('env') or definition.get('default_from_env')
        if name not in template_vars and env_key and os.environ.get(env_key) is not None:
          value = os.environ.get(env_key)
        resolved.append({
          "name": name,
          "value": value,
          "provided": name in template_vars,
          "default": definition.get('default'),
          "type": definition.get('type', 'string'),
          "required": definition.get('required', False),
          "description": definition.get('description') or definition.get('help'),
        })
        seen.add(name)
    for name, value in template_vars.items():
      if name not in seen:
        resolved.append({"name": name, "value": value, "provided": True, "declared": False})
    return resolved

  def _render_with_vars(self, with_vars, context, mappings):
    if not isinstance(with_vars, dict):
      return {}
    rendered = {}
    render_context = context.copy()
    if mappings:
      render_context['mappings'] = mappings
    for key, value in with_vars.items():
      rendered[key] = self._render(str(value), render_context)
    return rendered

  def _render(self, value, context):
    env = Environment(
      trim_blocks=True,
      block_start_string='{%@',
      block_end_string='@%}',
      variable_start_string='{{@',
      variable_end_string='@}}',
      comment_start_string='{#@',
      comment_end_string='@#}'
    )
    env.globals.update({
      'current_repo': get_current_repo,
      'uuid': gen_uuid,
      'now': now_iso,
      'env': env_get,
      'read_file': read_file,
    })
    env.filters.update({
      'latest_release': get_latest_release,
      'slugify': slugify,
      'default_branch': get_default_branch,
      'to_yaml': to_yaml,
      'from_yaml': from_yaml,
      'to_json': to_json,
      'from_json': from_json,
    })
    return env.from_string(value).render(context or {})

  def _is_remote(self, content_location):
    return str(content_location).startswith(self.REMOTE_PREFIXES)

  def _conflict_behavior(self, exists, content, file_strategy):
    if isinstance(content, dict):
      if content.get('skip'):
        return "skip (skip=true)"
      if content.get('skip_if_exists') and exists:
        return "skip (skip_if_exists=true)"
    if not exists:
      return "create"
    behaviors = {
      'overwrite': 'overwrite existing file',
      'skip': 'skip existing file',
      'append': 'append to existing file',
      'rename': 'write renamed file',
      'backup': 'backup then overwrite existing file',
    }
    return behaviors.get(file_strategy, f"apply {file_strategy} strategy")

  def _load_mappings(self, mapping_files):
    mappings = {}
    for mappings_file_path in mapping_files or []:
      if not os.path.exists(mappings_file_path):
        self.logger.error(f"Mappings file not found: {mappings_file_path}")
        continue
      with open(mappings_file_path, 'r') as mf:
        file_mappings = yaml.safe_load(mf) or {}
      mappings = self._deep_merge_dicts(mappings, file_mappings)
    return mappings

  def _deep_merge_dicts(self, dict1, dict2):
    result = dict1.copy()
    for key, value in dict2.items():
      if key in result and isinstance(result[key], dict) and isinstance(value, dict):
        result[key] = self._deep_merge_dicts(result[key], value)
      else:
        result[key] = value
    return result

  def _format_text(self, explanation):
    lines = [
      "Structure explanation",
      f"  Structure definition: {explanation['structure_definition']}",
      f"  Base path: {explanation['base_path']}",
      f"  File strategy: {explanation['file_strategy']}",
      "",
      "Variables:",
    ]
    if explanation['variables']:
      for variable in explanation['variables']:
        indent = "  " + ("  " * variable.get('depth', 0))
        marker = "provided" if variable.get('provided') else "default"
        value = variable.get('value')
        value_text = "<unset>" if value is None else value
        lines.append(f"{indent}- {variable['name']}: {value_text} ({marker})")
    else:
      lines.append("  - none")

    lines.extend(["", "Files:"])
    if explanation['files']:
      for file_entry in explanation['files']:
        indent = "  " + ("  " * file_entry.get('depth', 0))
        source = file_entry.get('source', 'inline')
        extra = f" from {file_entry['content_location']}" if file_entry.get('content_location') else ""
        lines.append(f"{indent}- {file_entry['path']} [{source}{extra}; {file_entry['conflict_behavior']}]")
    else:
      lines.append("  - none")

    lines.extend(["", "Folders and nested structures:"])
    if explanation['folders']:
      for folder_entry in explanation['folders']:
        indent = "  " + ("  " * folder_entry.get('depth', 0))
        structs = ", ".join(folder_entry.get('structs') or []) or "none"
        with_vars = folder_entry.get('with') or {}
        with_text = f" with {with_vars}" if with_vars else ""
        lines.append(f"{indent}- {folder_entry['path']} (nested structs: {structs}){with_text}")
    else:
      lines.append("  - none")

    lines.extend(["", "Remote files:"])
    if explanation['remote_files']:
      for remote in explanation['remote_files']:
        indent = "  " + ("  " * remote.get('depth', 0))
        lines.append(f"{indent}- {remote['path']} <= {remote['content_location']}")
    else:
      lines.append("  - none")

    lines.extend(["", "Hooks (not executed):"])
    for hook_type in ('pre', 'post'):
      hooks = explanation['hooks'][hook_type]
      if hooks:
        lines.append(f"  {hook_type}:")
        for hook in hooks:
          indent = "    " + ("  " * hook.get('depth', 0))
          lines.append(f"{indent}- {hook['command']}")
      else:
        lines.append(f"  {hook_type}: none")

    lines.extend(["", "Notes:"])
    for note in explanation['notes']:
      lines.append(f"  - {note}")
    return "\n".join(lines)
