from structkit.commands import Command
import os
import yaml
import argparse
from structkit.file_item import FileItem
from structkit.completers import file_strategy_completer, structures_completer
from structkit.template_renderer import TemplateRenderer

import subprocess


# Generate command class
class GenerateCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.description = "Generate the project structure from a YAML configuration file"
    structure_arg = parser.add_argument('structure_definition', nargs='?', default='.struct.yaml', type=str, help='Path to the YAML configuration file (default: .struct.yaml)')
    structure_arg.completer = structures_completer
    parser.add_argument('base_path', nargs='?', default='.', type=str, help='Base path where the structure will be created (default: current directory)')
    parser.add_argument(
      '-s',
      '--structures-path',
      type=str,
      help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
      default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
    )
    parser.add_argument('-n', '--input-store', type=str, help='Path to the input store (env: STRUCTKIT_INPUT_STORE)', default=os.getenv('STRUCTKIT_INPUT_STORE', '/tmp/structkit/input.json'))
    parser.add_argument('-d', '--dry-run', action='store_true', help='Perform a dry run without creating any files or directories')
    parser.add_argument('--diff', action='store_true', help='Show unified diffs for files that would change during dry-run or console output')
    parser.add_argument('-v', '--vars', type=str, help='Template variables in the format KEY1=value1,KEY2=value2')
    parser.add_argument('-b', '--backup', type=str, help='Path to the backup folder (env: STRUCTKIT_BACKUP_PATH)', default=os.getenv('STRUCTKIT_BACKUP_PATH', None))
    parser.add_argument(
      '-f',
      '--file-strategy',
      type=str,
      choices=['overwrite', 'skip', 'append', 'rename', 'backup'],
      default=os.getenv('STRUCTKIT_FILE_STRATEGY', 'overwrite'),
      help='Strategy for handling existing files (env: STRUCTKIT_FILE_STRATEGY)').completer = file_strategy_completer
    parser.add_argument('-p', '--global-system-prompt', type=str, help='Global system prompt for OpenAI (env: STRUCTKIT_GLOBAL_SYSTEM_PROMPT)', default=os.getenv('STRUCTKIT_GLOBAL_SYSTEM_PROMPT', None))
    parser.add_argument('--non-interactive', action='store_true', help='Run the command in non-interactive mode (env: STRUCTKIT_NON_INTERACTIVE)', default=os.getenv('STRUCTKIT_NON_INTERACTIVE', '').lower() in ('true', '1', 'yes'))
    parser.add_argument('--mappings-file', type=str, action='append',
                        help='Path to a YAML file containing mappings to be used in templates (can be specified multiple times)')
    parser.add_argument('-o', '--output', type=str,
                        choices=['console', 'file'], default=os.getenv('STRUCTKIT_OUTPUT_MODE', 'file'), help='Output mode (env: STRUCTKIT_OUTPUT_MODE)')
    parser.set_defaults(func=self.execute)

  def _parse_template_vars(self, vars_str):
    """Parse a comma-separated KEY=VALUE string into a dict safely.
    - Ignores empty tokens and trailing commas
    - Supports values containing '=' by splitting only on the first '='
    - Logs and skips malformed entries without raising
    """
    result = {}
    if not vars_str:
      return result
    # Normalize by removing accidental leading/trailing commas and whitespace
    tokens = [t.strip() for t in vars_str.strip(', ').split(',')]
    for token in tokens:
      if not token:
        continue
      if '=' not in token:
        # Skip malformed item but warn
        self.logger.warning(f"Skipping malformed template var (no '='): '{token}'")
        continue
      key, value = token.split('=', 1)
      key = key.strip()
      value = value
      if not key:
        self.logger.warning(f"Skipping template var with empty key: '{token}'")
        continue
      result[key] = value
    return result

  def _deep_merge_dicts(self, dict1, dict2):
    """
    Deep merge two dictionaries, with dict2 values overriding dict1 values.
    """
    result = dict1.copy()
    for key, value in dict2.items():
      if key in result and isinstance(result[key], dict) and isinstance(value, dict):
        result[key] = self._deep_merge_dicts(result[key], value)
      else:
        result[key] = value
    return result

  def _run_hooks(self, hooks, hook_type="pre"):  # helper for running hooks
    if not hooks:
      return True
    for cmd in hooks:
      self.logger.info(f"Running {hook_type}-hook: {cmd}")
      try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
          self.logger.info(f"{hook_type}-hook stdout: {result.stdout.strip()}")
        if result.stderr:
          self.logger.info(f"{hook_type}-hook stderr: {result.stderr.strip()}")
      except subprocess.CalledProcessError as e:
        self.logger.error(f"{hook_type}-hook failed: {cmd}")
        self.logger.error(f"Return code: {e.returncode}")
        if e.stdout:
          self.logger.error(f"stdout: {e.stdout.strip()}")
        if e.stderr:
          self.logger.error(f"stderr: {e.stderr.strip()}")
        return False
    return True

  def _load_yaml_config(self, structure_definition, structures_path):
    if structure_definition.endswith(".yaml") and not structure_definition.startswith("file://"):
      structure_definition = f"file://{structure_definition}"

    if structure_definition.startswith("file://") and structure_definition.endswith(".yaml"):
      with open(structure_definition[7:], 'r') as f:
        return yaml.safe_load(f)
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
        return None
      with open(file_path, 'r') as f:
        return yaml.safe_load(f)

  def execute(self, args):
    # Log when using STRUCTKIT_STRUCTURES_PATH environment variable
    if args.structures_path and args.structures_path == os.getenv('STRUCTKIT_STRUCTURES_PATH'):
      self.logger.info(f"Using STRUCTKIT_STRUCTURES_PATH: {args.structures_path}")

    self.logger.info("Generating structure")
    self.logger.info(f"  Structure definition: {args.structure_definition}")
    self.logger.info(f"  Base path: {args.base_path}")

    # Load mappings if provided
    mappings = {}
    if getattr(args, 'mappings_file', None):
      for mappings_file_path in args.mappings_file:
        if os.path.exists(mappings_file_path):
          self.logger.info(f"Loading mappings from: {mappings_file_path}")
          with open(mappings_file_path, 'r') as mf:
            try:
              file_mappings = yaml.safe_load(mf) or {}
              # Deep merge the mappings, with later files overriding earlier ones
              mappings = self._deep_merge_dicts(mappings, file_mappings)
            except Exception as e:
              self.logger.error(f"Failed to load mappings file {mappings_file_path}: {e}")
              return
        else:
          self.logger.error(f"Mappings file not found: {mappings_file_path}")
          return

    if args.backup and not os.path.exists(args.backup):
      os.makedirs(args.backup)

    if args.base_path and not os.path.exists(args.base_path) and "console" not in args.output:
      self.logger.info(f"Creating base path: {args.base_path}")
      os.makedirs(args.base_path)

    # Load config to check for hooks
    config = None
    config = self._load_yaml_config(args.structure_definition, args.structures_path)
    if config is None:
      return

    pre_hooks = config.get('pre_hooks', [])
    post_hooks = config.get('post_hooks', [])

    # Run pre-hooks
    if not self._run_hooks(pre_hooks, hook_type="pre"):
      self.logger.error("Aborting generation due to pre-hook failure.")
      return

    # Actually generate structure
    self._create_structure(args, mappings)

    # Run post-hooks
    if not self._run_hooks(post_hooks, hook_type="post"):
      self.logger.error("Post-hook failed.")
      return

  def _create_structure(self, args, mappings=None, summary=None, print_summary=True):
    if isinstance(args, dict):
        args = argparse.Namespace(**args)

    config = self._load_yaml_config(args.structure_definition, args.structures_path)
    if config is None:
      return summary if summary is not None else None

    # Safely parse template variables
    template_vars = self._parse_template_vars(args.vars) if getattr(args, 'vars', None) else {}
    config_structure = config.get('files', config.get('structure', []))
    config_folders = config.get('folders', [])
    config_variables = config.get('variables', [])

    # Action counters for final summary (initialize once and reuse across recursive calls)
    if summary is None:
      summary = {
          "created": 0,
          "updated": 0,
          "appended": 0,
          "skipped": 0,
          "backed_up": 0,
          "renamed": 0,
          "folders": 0,
          "dry_run_created": 0,
          "dry_run_updated": 0,
      }

    for item in config_structure:
      self.logger.debug(f"Processing item: {item}")
      for name, content in item.items():
        self.logger.debug(f"Processing name: {name}, content: {content}")
        if isinstance(content, dict):
          content["name"] = name
          content["global_system_prompt"] = args.global_system_prompt
          content["config_variables"] = config_variables
          content["input_store"] = args.input_store
          content["non_interactive"] = args.non_interactive
          content["mappings"] = mappings or {}
          file_item = FileItem(content)
          file_item.fetch_content()
        elif isinstance(content, str):
          file_item = FileItem(
            {
              "name": name,
              "content": content,
              "config_variables": config_variables,
              "input_store": args.input_store,
              "non_interactive": args.non_interactive,
              "mappings": mappings or {},
            }
          )

        # Determine the full file path
        file_path_to_create = os.path.join(args.base_path, name)
        existing_content = None
        if os.path.exists(file_path_to_create):
          self.logger.info(f"ℹ️  Exists: {file_path_to_create}")
          with open(file_path_to_create, 'r') as existing_file:
            existing_content = existing_file.read()

        file_item.process_prompt(
          args.dry_run,
          existing_content=existing_content
        )
        file_item.apply_template_variables(template_vars)

        # Output mode logic with diff support
        if hasattr(args, 'output') and args.output == 'console':
          print(f"=== {file_path_to_create} ===")
          if args.diff and existing_content is not None:
            import difflib
            new_content = file_item.content if file_item.content.endswith("\n") else file_item.content + "\n"
            old_content = existing_content if existing_content.endswith("\n") else existing_content + "\n"
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path_to_create}",
                tofile=f"b/{file_path_to_create}",
            )
            print("".join(diff))
          else:
            print(file_item.content)
        else:
          # When dry-run with --diff and files mode, print action and diff instead of writing
          if args.dry_run and args.diff:
            action = "create"
            if existing_content is not None:
              action = "update"
            print(f"[DRY RUN] {action}: {file_path_to_create}")
            if action == "create":
              summary["dry_run_created"] += 1
            else:
              summary["dry_run_updated"] += 1
            import difflib
            new_content = file_item.content if file_item.content.endswith("\n") else file_item.content + "\n"
            old_content = (existing_content if existing_content is not None else "")
            old_content = old_content if old_content.endswith("\n") else (old_content + ("\n" if old_content else ""))
            diff = difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{file_path_to_create}",
                tofile=f"b/{file_path_to_create}",
            )
            print("".join(diff))
          else:
            result = file_item.create(
                args.base_path,
                args.dry_run or False,
                args.backup or None,
                args.file_strategy or 'overwrite'
            )
            if isinstance(result, dict):
              if result.get("action") == "created":
                summary["created"] += 1
              elif result.get("action") == "updated":
                summary["updated"] += 1
              elif result.get("action") == "appended":
                summary["appended"] += 1
              elif result.get("action") == "skipped":
                summary["skipped"] += 1
              if result.get("backed_up_to"):
                summary["backed_up"] += 1
              if result.get("renamed_from"):
                summary["renamed"] += 1

    for item in config_folders:
      for folder, content in item.items():
        folder_path = os.path.join(args.base_path, folder)
        if hasattr(args, 'output') and args.output == 'file':
          os.makedirs(folder_path, exist_ok=True)
          self.logger.info(f"📁 Created folder: {folder_path}")
          summary["folders"] += 1

        # check if content has structkit value
        if 'struct' in content:
          self.logger.info("Generating structure")
          self.logger.info(f"  Folder: {folder}")
          self.logger.info("  Struct(s):")
          if isinstance(content['struct'], list):
            # iterate over the list of structures
            for struct in content['struct']:
              self.logger.info(f"    - {struct}")
          if isinstance(content['struct'], str):
            self.logger.info(f"    - {content['struct']}")

          # get vars from with param. this will be a dict of key value pairs
          merged_vars = ""

          # dict to comma separated string
          if 'with' in content:
            if isinstance(content['with'], dict):
              # Render Jinja2 expressions in each value using TemplateRenderer
              rendered_with = {}
              renderer = TemplateRenderer(
                  config_variables, args.input_store, args.non_interactive, mappings)
              for k, v in content['with'].items():
                # Render the value as a template, passing in mappings and template_vars
                context = template_vars.copy() if template_vars else {}
                context['mappings'] = mappings or {}
                rendered_with[k] = renderer.render_template(str(v), context)
              merged_vars = ",".join(
                  [f"{k}={v}" for k, v in rendered_with.items()])

          # Merge parent args.vars safely without introducing trailing commas
          if getattr(args, 'vars', None):
            parts = []
            parent_vars = args.vars.strip().strip(',')
            if parent_vars:
              parts.append(parent_vars)
            if merged_vars:
              parts.append(merged_vars)
            merged_vars = ",".join(parts)

          # If nothing to merge, keep None to avoid accidental truthiness with empty string
          merged_vars = merged_vars if merged_vars else None

          if isinstance(content['struct'], str):
            self._create_structure({
              'structure_definition': content['struct'],
              'base_path': folder_path,
              'structures_path': args.structures_path,
              'dry_run': args.dry_run,
              'diff': getattr(args, 'diff', False),
              'output': getattr(args, 'output', 'file'),
              'vars': merged_vars,
              'backup': args.backup,
              'file_strategy': args.file_strategy,
              'global_system_prompt': args.global_system_prompt,
              'input_store': args.input_store,
              'non_interactive': args.non_interactive,
            }, mappings=mappings, summary=summary, print_summary=False)
          elif isinstance(content['struct'], list):
            for struct in content['struct']:
              self._create_structure({
                'structure_definition': struct,
                'base_path': folder_path,
                'structures_path': args.structures_path,
                'dry_run': args.dry_run,
                'diff': getattr(args, 'diff', False),
                'output': getattr(args, 'output', 'file'),
                'vars': merged_vars,
                'backup': args.backup,
                'file_strategy': args.file_strategy,
                'global_system_prompt': args.global_system_prompt,
                'input_store': args.input_store,
                'non_interactive': args.non_interactive,
              }, mappings=mappings, summary=summary, print_summary=False)
        else:
          self.logger.warning(f"Unsupported content in folder: {folder}")

    # Final summary (only once for top-level call)
    if print_summary:
      self.logger.info("")
      self.logger.info("Summary of actions:")
      self.logger.info(f"  ✅  Created: {summary['created']}")
      self.logger.info(f"  ✅  Updated: {summary['updated']}")
      self.logger.info(f"  📝  Appended: {summary['appended']}")
      self.logger.info(f"  ⏭️  Skipped: {summary['skipped']}")
      self.logger.info(f"  🗄️  Backed up: {summary['backed_up']}")
      self.logger.info(f"  🔁  Renamed: {summary['renamed']}")
      self.logger.info(f"  📁  Folders created: {summary['folders']}")
      if args.dry_run:
        self.logger.info(
            f"  [DRY RUN] Would create: {summary['dry_run_created']}")
        self.logger.info(
            f"  [DRY RUN] Would update: {summary['dry_run_updated']}")

    return summary
