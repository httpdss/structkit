import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from structkit.commands import Command
from structkit.completers import file_strategy_completer, structures_completer
from structkit.template_renderer import TemplateRenderer


class ExplainCommand(Command):
    """Explain how a structure definition resolves without creating anything."""

    def __init__(self, parser):
      super().__init__(parser)
      parser.description = "Preview how a structure definition resolves without generating files"
      structure_arg = parser.add_argument('structure_definition', type=str, help='Structure definition name or path to a YAML file')
      structure_arg.completer = structures_completer
      parser.add_argument('base_path', nargs='?', default='.', type=str, help='Base path used to resolve generated paths and conflicts (default: current directory)')
      parser.add_argument(
        '-s',
        '--structures-path',
        type=str,
        help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
        default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
      )
      parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
      parser.add_argument(
        '-f',
        '--file-strategy',
        type=str,
        choices=['overwrite', 'skip', 'append', 'rename', 'backup'],
        default=os.getenv('STRUCTKIT_FILE_STRATEGY', 'overwrite'),
        help='Strategy to report when generated files already exist (env: STRUCTKIT_FILE_STRATEGY)').completer = file_strategy_completer
      parser.add_argument('--json', action='store_true', help='Output the explanation as JSON')
      parser.set_defaults(func=self.execute)

    def execute(self, args):
      explanation = self.explain(
        args.structure_definition,
        args.base_path,
        structures_path=args.structures_path,
        vars_str=args.vars,
        file_strategy=args.file_strategy,
      )
      if args.json:
        print(json.dumps(explanation, indent=2))
      else:
        print(self.format_text(explanation))

    def explain(
        self,
        structure_definition: str,
        base_path: str = '.',
        structures_path: Optional[str] = None,
        vars_str: Optional[str] = None,
        file_strategy: str = 'overwrite',
    ) -> Dict[str, Any]:
      provided_vars = self._parse_template_vars(vars_str)
      context = {
        'structures_path': structures_path,
        'provided_vars': provided_vars,
        'input_store': '/tmp/structkit/input.json',
        'non_interactive': True,
        'file_strategy': file_strategy,
      }
      explanation = {
        'structure': structure_definition,
        'base_path': base_path,
        'file_strategy': file_strategy,
        'creates_files': False,
        'executes_hooks': False,
        'variables': [],
        'hooks': {'pre': [], 'post': []},
        'files': [],
        'folders': [],
        'nested_structures': [],
        'remote_files': [],
        'warnings': [],
      }
      self._collect(structure_definition, base_path, context, explanation, set(), path=[structure_definition])
      return explanation

    def format_text(self, explanation: Dict[str, Any]) -> str:
      lines = [
        f"Structure explanation: {explanation['structure']}",
        f"Base path: {explanation['base_path']}",
        f"File strategy: {explanation['file_strategy']}",
        "Safety: no files or folders will be created, and hooks will not be executed.",
        "",
      ]

      lines.append("Variables:")
      if explanation['variables']:
        for variable in explanation['variables']:
          value = variable.get('resolved_value')
          value_text = '<unresolved>' if value is None else str(value)
          default = variable.get('default')
          default_text = '' if default is None else f" default={default}"
          lines.append(f"  - {variable['name']}: value={value_text}{default_text} source={variable.get('source', 'unknown')}")
      else:
        lines.append("  - none")

      lines.append("")
      lines.append("Hooks (not executed):")
      hooks = explanation['hooks']
      if hooks['pre'] or hooks['post']:
        for hook in hooks['pre']:
          lines.append(f"  - pre: {hook['command']} ({hook['structure']})")
        for hook in hooks['post']:
          lines.append(f"  - post: {hook['command']} ({hook['structure']})")
      else:
        lines.append("  - none")

      lines.append("")
      lines.append("Folders:")
      if explanation['folders']:
        for folder in explanation['folders']:
          lines.append(f"  - {folder['path']}")
      else:
        lines.append("  - none")

      lines.append("")
      lines.append("Files:")
      if explanation['files']:
        for file_info in explanation['files']:
          remote = f" remote={file_info['remote']}" if file_info.get('remote') else ''
          lines.append(f"  - {file_info['path']} action={file_info['conflict_action']}{remote}")
      else:
        lines.append("  - none")

      lines.append("")
      lines.append("Nested structures:")
      if explanation['nested_structures']:
        for nested in explanation['nested_structures']:
          vars_text = ''
          if nested.get('vars'):
            vars_text = " with " + ",".join(f"{k}={v}" for k, v in nested['vars'].items())
          lines.append(f"  - {nested['structure']} -> {nested['base_path']}{vars_text}")
      else:
        lines.append("  - none")

      lines.append("")
      lines.append("Remote files:")
      if explanation['remote_files']:
        for remote in explanation['remote_files']:
          lines.append(f"  - {remote['file']} -> {remote['path']}")
      else:
        lines.append("  - none")

      if explanation['warnings']:
        lines.append("")
        lines.append("Warnings:")
        for warning in explanation['warnings']:
          lines.append(f"  - {warning}")

      return "\n".join(lines)

    def _collect(
        self,
        structure_definition: str,
        base_path: str,
        context: Dict[str, Any],
        explanation: Dict[str, Any],
        seen: Set[Tuple[str, str]],
        path: List[str],
    ):
      config, source = self._load_yaml_config(structure_definition, context['structures_path'])
      if config is None:
        explanation['warnings'].append(f"Structure not found or could not be loaded: {structure_definition}")
        return
      if not isinstance(config, dict):
        explanation['warnings'].append(f"Structure is not a mapping: {structure_definition}")
        return

      key = (source or structure_definition, os.path.abspath(base_path))
      if key in seen:
        explanation['warnings'].append(f"Skipped recursive structure reference: {' -> '.join(path)}")
        return
      seen.add(key)

      variables = config.get('variables', []) or []
      resolved_vars = self._resolve_variables(variables, context['provided_vars'])
      self._append_variables(explanation, structure_definition, variables, resolved_vars, context['provided_vars'])

      for command in config.get('pre_hooks', []) or []:
        explanation['hooks']['pre'].append({'structure': structure_definition, 'command': command})
      for command in config.get('post_hooks', []) or []:
        explanation['hooks']['post'].append({'structure': structure_definition, 'command': command})

      files = config.get('files', config.get('structure', [])) or []
      for item in files:
        if not isinstance(item, dict):
          explanation['warnings'].append(f"Unsupported file entry in {structure_definition}: {item}")
          continue
        for name, content in item.items():
          rendered_name = self._render_value(str(name), variables, resolved_vars)
          file_path = os.path.normpath(os.path.join(base_path, rendered_name))
          remote = content.get('file') if isinstance(content, dict) else None
          skip = bool(isinstance(content, dict) and content.get('skip', False))
          skip_if_exists = bool(isinstance(content, dict) and content.get('skip_if_exists', False))
          conflict_action = self._conflict_action(file_path, context['file_strategy'], skip, skip_if_exists)
          file_info = {
            'structure': structure_definition,
            'name': rendered_name,
            'path': file_path,
            'exists': os.path.exists(file_path),
            'conflict_action': conflict_action,
            'remote': remote,
            'has_prompt': bool(isinstance(content, dict) and content.get('user_prompt')),
            'skip': skip,
            'skip_if_exists': skip_if_exists,
          }
          explanation['files'].append(file_info)
          if remote:
            explanation['remote_files'].append({'structure': structure_definition, 'file': remote, 'path': file_path})

      folders = config.get('folders', []) or []
      for item in folders:
        if not isinstance(item, dict):
          folder_path = os.path.normpath(os.path.join(base_path, str(item)))
          explanation['folders'].append({'structure': structure_definition, 'name': str(item), 'path': folder_path})
          continue
        for folder, content in item.items():
          rendered_folder = self._render_value(str(folder), variables, resolved_vars)
          folder_path = os.path.normpath(os.path.join(base_path, rendered_folder))
          explanation['folders'].append({'structure': structure_definition, 'name': rendered_folder, 'path': folder_path})
          if not isinstance(content, dict):
            continue

          with_vars = self._render_with_vars(content.get('with', {}), variables, resolved_vars)
          nested_vars = context['provided_vars'].copy()
          nested_vars.update(with_vars)
          structs = content.get('struct') or content.get('structkit')
          if isinstance(structs, str):
            structs = [structs]
          if isinstance(structs, list):
            for nested_struct in structs:
              explanation['nested_structures'].append({
                'structure': nested_struct,
                'base_path': folder_path,
                'parent': structure_definition,
                'vars': with_vars,
              })
              nested_context = context.copy()
              nested_context['provided_vars'] = nested_vars
              self._collect(nested_struct, folder_path, nested_context, explanation, seen, path + [nested_struct])

      seen.remove(key)

    def _load_yaml_config(self, structure_definition, structures_path):
      if structure_definition.endswith((".yaml", ".yml")) and not structure_definition.startswith("file://"):
        structure_definition = f"file://{structure_definition}"

      if structure_definition.startswith("file://") and structure_definition.endswith((".yaml", ".yml")):
        file_path = structure_definition[7:]
      else:
        this_file = os.path.dirname(os.path.realpath(__file__))
        contribs_path = os.path.join(this_file, "..", "contribs")
        file_path = os.path.join(contribs_path, f"{structure_definition}.yaml")
        if structures_path:
          file_path = os.path.join(structures_path, f"{structure_definition}.yaml")
        if not os.path.exists(file_path):
          file_path = os.path.join(contribs_path, f"{structure_definition}.yaml")

      if not os.path.exists(file_path):
        self.logger.error(f"❗ File not found: {file_path}")
        return None, file_path

      try:
        with open(file_path, 'r') as f:
          return yaml.safe_load(f) or {}, file_path
      except (yaml.YAMLError, OSError) as exc:
        self.logger.error(f"❗ Failed to load {file_path}: {exc}")
        return None, file_path

    def _parse_template_vars(self, vars_str):
      result = {}
      if not vars_str:
        return result
      for token in [t.strip() for t in vars_str.strip(', ').split(',')]:
        if not token or '=' not in token:
          continue
        key, value = token.split('=', 1)
        key = key.strip()
        if key:
          result[key] = value
      return result

    def _resolve_variables(self, variables, provided_vars):
      resolved = {}
      for item in variables:
        if not isinstance(item, dict):
          continue
        for name, content in item.items():
          content = content or {}
          if name in provided_vars:
            resolved[name] = provided_vars[name]
          elif isinstance(content, dict) and 'default' in content:
            resolved[name] = content.get('default')
          elif isinstance(content, dict) and (content.get('env') or content.get('default_from_env')):
            env_key = content.get('env') or content.get('default_from_env')
            if os.getenv(env_key) is not None:
              resolved[name] = os.getenv(env_key)
      for name, value in provided_vars.items():
        resolved.setdefault(name, value)
      return resolved

    def _append_variables(self, explanation, structure_definition, variables, resolved_vars, provided_vars):
      existing = {(item['structure'], item['name']) for item in explanation['variables']}
      for item in variables:
        if not isinstance(item, dict):
          continue
        for name, content in item.items():
          if (structure_definition, name) in existing:
            continue
          content = content or {}
          source = 'provided' if name in provided_vars else ('default' if isinstance(content, dict) and 'default' in content else 'unresolved')
          if isinstance(content, dict) and source == 'unresolved' and (content.get('env') or content.get('default_from_env')):
            env_key = content.get('env') or content.get('default_from_env')
            source = f"env:{env_key}" if os.getenv(env_key) is not None else source
          explanation['variables'].append({
            'structure': structure_definition,
            'name': name,
            'type': content.get('type', '') if isinstance(content, dict) else '',
            'default': content.get('default') if isinstance(content, dict) and 'default' in content else None,
            'required': bool(content.get('required', False)) if isinstance(content, dict) else False,
            'resolved_value': resolved_vars.get(name),
            'source': source,
          })

    def _render_value(self, value, variables, resolved_vars):
      try:
        renderer = TemplateRenderer(variables, '/tmp/structkit/explain-input.json', True, {})
        return renderer.render_template(value, resolved_vars)
      except Exception as exc:
        return f"{value} [unresolved: {exc}]"

    def _render_with_vars(self, with_config, variables, resolved_vars):
      if not isinstance(with_config, dict):
        return {}
      rendered = {}
      for key, value in with_config.items():
        rendered[key] = self._render_value(str(value), variables, resolved_vars)
      return rendered

    def _conflict_action(self, path, file_strategy, skip=False, skip_if_exists=False):
      exists = os.path.exists(path)
      if skip:
        return 'skip (skip=true)'
      if skip_if_exists and exists:
        return 'skip existing file (skip_if_exists=true)'
      if not exists:
        return 'create'
      return {
        'overwrite': 'overwrite existing file',
        'skip': 'skip existing file',
        'append': 'append to existing file',
        'rename': 'rename new file',
        'backup': 'backup and overwrite existing file',
      }.get(file_strategy, file_strategy)
