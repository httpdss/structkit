import yaml
from dotenv import load_dotenv
from structkit.commands import Command

load_dotenv()


# Validate command class
class ValidateCommand(Command):
    def __init__(self, parser):
      super().__init__(parser)
      parser.description = "Validate a YAML configuration file for structure definitions"
      parser.add_argument('yaml_file', type=str, help='Path to the YAML configuration file')
      parser.set_defaults(func=self.execute)

    def execute(self, args):
      self.logger.info(f"Validating {args.yaml_file}")

      with open(args.yaml_file, 'r') as f:
        config = yaml.safe_load(f)

      # Validate pre_hooks and post_hooks if present
      for hook_key in ["pre_hooks", "post_hooks"]:
        if hook_key in config:
          if not isinstance(config[hook_key], list):
            raise ValueError(f"The '{hook_key}' key must be a list of shell commands (strings).")
          for cmd in config[hook_key]:
            if not isinstance(cmd, str):
              raise ValueError(f"Each item in '{hook_key}' must be a string (shell command).")

      if 'structure' in config and 'files' in config:
          self.logger.warning("Both 'structure' and 'files' keys exist. Prioritizing 'structure'.")
      self._validate_structure_config(config.get('structure') or config.get('files', []))
      self._validate_folders_config(config.get('folders', []))
      self._validate_variables_config(config.get('variables', []))

    # Validate the 'folders' key in the configuration file
    # folders should be defined as a list of dictionaries
    # each dictionary should have a 'struct' key
    #
    # Example:
    # folders:
    #   - .devops/modules/my_module_one:
    #       struct: terraform/module
    #   - .devops/modules/my_module_two:
    #       struct: terraform/module
    #       with:
    #         module_name: my_module_two
    def _validate_folders_config(self, folders):
      if not isinstance(folders, list):
        raise ValueError("The 'folders' key must be a list.")
      for item in folders:
        if not isinstance(item, dict):
            raise ValueError("Each item in the 'folders' list must be a dictionary.")
        for name, content in item.items():
            if not isinstance(name, str):
              raise ValueError("Each name in the 'folders' item must be a string.")
            if not isinstance(content, dict):
              raise ValueError(f"The content of '{name}' must be a dictionary.")
            if 'struct' not in content:
              raise ValueError(f"Dictionary item '{name}' must contain a 'struct' key.")
            if not isinstance(content['struct'], str) and not isinstance(content['struct'], list):
              raise ValueError(f"The 'struct' value for '{name}' must be a string.")
            if 'with' in content and not isinstance(content['with'], dict):
              raise ValueError(f"The 'with' value for '{name}' must be a dictionary.")

    # Validate the 'variables' key in the configuration file
    # variables should be defined as a list of dictionaries
    # each dictionary should have a 'name' key and optionall 'default' value
    #
    # Example:
    # variables:
    #   - session_name:
    #       type: string
    #       default: my_session
    #   - project_name:
    #       type: string
    #       default: my_project
    #       help: The name of the project
    def _validate_variables_config(self, variables):
      if not isinstance(variables, list):
        raise ValueError("The 'variables' key must be a list.")
      for item in variables:
        if not isinstance(item, dict):
            raise ValueError("Each item in the 'variables' list must be a dictionary.")
        for name, content in item.items():
            if not isinstance(name, str):
              raise ValueError("Each name in the 'variables' item must be a string.")
            if not isinstance(content, dict):
              raise ValueError(f"The content of '{name}' must be a dictionary.")
            if 'type' not in content:
              raise ValueError(f"Dictionary item '{name}' must contain a 'type' key.")
            if content['type'] not in ['string', 'number', 'boolean']:
              raise ValueError(f"Invalid type for '{name}'. Must be 'string', 'number' or 'boolean'.")
            if 'default' in content and content['type'] == 'boolean' and not isinstance(content['default'], bool):
              raise ValueError(f"Invalid default value for '{name}'. Must be a boolean.")

    def _validate_structure_config(self, structure):
      if not isinstance(structure, list):
        raise ValueError("The 'structure' key must be a list.")
      for item in structure:
        if not isinstance(item, dict):
            raise ValueError("Each item in the 'structure' list must be a dictionary.")
        for name, content in item.items():
            if not isinstance(name, str):
              raise ValueError("Each name in the 'structure' item must be a string.")
            if isinstance(content, dict):
              # Check that any of the keys 'content', 'file' or 'prompt' is present
              if 'content' not in content and 'file' not in content and 'user_prompt' not in content:
                raise ValueError(f"Dictionary item '{name}' must contain either 'content' or 'file' or 'user_prompt' key.")
              # Check if 'file' key is present and its value is a string
              if 'file' in content and not isinstance(content['file'], str):
                raise ValueError(f"The 'file' value for '{name}' must be a string.")
              # Check if 'permissions' key is present and its value is a string
              if 'permissions' in content and not isinstance(content['permissions'], str):
                raise ValueError(f"The 'permissions' value for '{name}' must be a string.")
              # Check if 'prompt' key is present and its value is a string
              if 'prompt' in content and not isinstance(content['prompt'], str):
                raise ValueError(f"The 'prompt' value for '{name}' must be a string.")
              if 'skip' in content and not isinstance(content['skip'], bool):
                raise ValueError(f"The 'skip' value for '{name}' must be a string.")
              if 'skip_if_exists' in content and not isinstance(content['skip_if_exists'], bool):
                raise ValueError(f"The 'skip_if_exists' value for '{name}' must be a string.")
            elif not isinstance(content, str):
              raise ValueError(f"The content of '{name}' must be a string or dictionary.")
      self.logger.info("Configuration validation passed.")
