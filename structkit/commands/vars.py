import json
import os
import yaml

from structkit.commands import Command
from structkit.completers import structures_completer


class VarsCommand(Command):
    """Inspect variables declared by a structure definition."""

    def __init__(self, parser):
      super().__init__(parser)
      parser.description = "Inspect variables declared by a structure definition"
      structure_arg = parser.add_argument('structure_definition', type=str, help='Structure definition name or path to a YAML file')
      structure_arg.completer = structures_completer
      parser.add_argument(
        '-s',
        '--structures-path',
        type=str,
        help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
        default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
      )
      parser.add_argument('--json', action='store_true', help='Output variables as JSON')
      parser.set_defaults(func=self.execute)

    def execute(self, args):
      config = self._load_yaml_config(args.structure_definition, args.structures_path)
      if config is None:
        raise SystemExit(1)
      if not isinstance(config, dict):
        self.logger.error("❗ Invalid structure config: top-level YAML content must be a mapping")
        raise SystemExit(1)

      try:
        variables = self._normalize_variables(config.get('variables', []))
      except ValueError as exc:
        self.logger.error(f"❗ Invalid variables config: {exc}")
        raise SystemExit(1) from exc

      if args.json:
        print(json.dumps(variables, indent=2))
      else:
        self._print_text(args.structure_definition, variables)

    def _load_yaml_config(self, structure_definition, structures_path):
      if structure_definition.endswith(('.yaml', '.yml')) and not structure_definition.startswith("file://"):
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
        return None

      try:
        with open(file_path, 'r') as f:
          return yaml.safe_load(f) or {}
      except yaml.YAMLError as exc:
        self.logger.error(f"❗ Invalid YAML in {file_path}: {exc}")
        return None
      except OSError as exc:
        self.logger.error(f"❗ Failed to read {file_path}: {exc}")
        return None

    def _normalize_variables(self, variables):
      if variables is None:
        return []
      if not isinstance(variables, list):
        raise ValueError("the 'variables' key must be a list")

      normalized = []
      for item in variables:
        if not isinstance(item, dict):
          raise ValueError("each variable entry must be a mapping")
        for name, content in item.items():
          if not isinstance(name, str):
            raise ValueError("each variable name must be a string")
          if content is None:
            content = {}
          if not isinstance(content, dict):
            raise ValueError(f"the content of '{name}' must be a mapping")

          has_default = 'default' in content
          description = content.get('description', content.get('help', ''))
          normalized.append({
            'name': name,
            'type': content.get('type', ''),
            'default': content.get('default') if has_default else None,
            'description': description if description is not None else '',
            'required': bool(content.get('required', False)),
          })
      return normalized

    def _print_text(self, structure_definition, variables):
      print(f"Variables for {structure_definition}")
      if not variables:
        print("No variables defined.")
        return

      rows = [[
        variable['name'],
        variable['type'] or '-',
        self._format_default(variable['default']),
        'required' if variable['required'] else 'optional',
        variable['description'] or '-',
      ] for variable in variables]
      headers = ['Name', 'Type', 'Default', 'Required', 'Description']
      widths = [len(header) for header in headers]
      for row in rows:
        for index, value in enumerate(row):
          widths[index] = max(widths[index], len(value))

      print("  " + "  ".join(header.ljust(widths[index]) for index, header in enumerate(headers)))
      print("  " + "  ".join("-" * width for width in widths))
      for row in rows:
        print("  " + "  ".join(value.ljust(widths[index]) for index, value in enumerate(row)))

    def _format_default(self, value):
      if value is None:
        return '-'
      if isinstance(value, bool):
        return str(value).lower()
      return str(value)
