"""Configuration layering system for structkit.

Supports loading and merging configuration from multiple sources:
1. Built-in defaults
2. User config (~/.config/struct/config.yaml)
3. Project config (.structkit.yaml, legacy .struct.yaml, or --config-file)
4. CLI arguments

Priority order: CLI args > Project config > User config > Built-in defaults
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


def get_user_config_path() -> Path:
    """Get the path to the user config file.

    Returns ~/.config/struct/config.yaml
    """
    return Path.home() / ".config" / "struct" / "config.yaml"


def get_builtin_defaults() -> Dict[str, Any]:
    """Return built-in default configuration values.

    These are the lowest priority defaults used when no other config is provided.
    """
    return {
        'file_strategy': 'overwrite',
        'input_store': '/tmp/structkit/input.json',
        'log': 'INFO',
        'non_interactive': False,
        'output': 'file',
    }


def load_yaml_config(config_path: str) -> Optional[Dict[str, Any]]:
    """Load a YAML config file and return its contents.

    Args:
        config_path: Path to the YAML config file

    Returns:
        Dictionary with config values, or None if file doesn't exist or is empty
    """
    if not config_path or not os.path.exists(config_path):
        return None

    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            if config is None:
                return {}
            if not isinstance(config, dict):
                logger.warning(f"Config file {config_path} does not contain a mapping, ignoring")
                return {}
            return config
    except yaml.YAMLError as exc:
        logger.warning(f"Failed to parse YAML in {config_path}: {exc}")
        return {}
    except OSError as exc:
        logger.warning(f"Failed to read {config_path}: {exc}")
        return {}


def merge_config_layer(base: Dict[str, Any], override: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge an override config layer into a base config.

    Override values take precedence over base values. Only merges top-level keys.

    Args:
        base: Base configuration dictionary
        override: Override configuration dictionary (can be None)

    Returns:
        Merged configuration dictionary
    """
    if override is None:
        return base.copy()

    result = base.copy()
    for key, value in override.items():
        if value is not None:
            result[key] = value
    return result


def load_layered_config(project_config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from all layers and merge them.

    Merge order (lowest to highest priority):
    1. Built-in defaults
    2. User config (~/.config/struct/config.yaml)
    3. Project config (if provided)

    Args:
        project_config_path: Path to project-specific config file

    Returns:
        Merged configuration dictionary
    """
    # Start with built-in defaults
    config = get_builtin_defaults()

    # Layer in user config
    user_config_path = get_user_config_path()
    if user_config_path.exists():
        logger.debug(f"Loading user config from {user_config_path}")
        user_config = load_yaml_config(str(user_config_path))
        config = merge_config_layer(config, user_config)

    # Layer in project config
    if project_config_path:
        logger.debug(f"Loading project config from {project_config_path}")
        project_config = load_yaml_config(project_config_path)
        config = merge_config_layer(config, project_config)

    return config


def merge_cli_args(config: Dict[str, Any], args) -> Dict[str, Any]:
    """Merge CLI arguments into configuration, giving CLI args highest priority.

    Args:
        config: Configuration dictionary from layered config files
        args: argparse Namespace with CLI arguments

    Returns:
        Final merged configuration dictionary
    """
    result = config.copy()
    args_dict = vars(args)

    # List of config keys that can be set via CLI args
    # We only override config file values if the CLI arg was explicitly provided
    # (i.e., it's not None and differs from the default)
    cli_overridable_keys = [
        'structures_path',
        'input_store',
        'file_strategy',
        'backup',
        'global_system_prompt',
        'non_interactive',
        'output',
        'log',
        'log_file',
        'source',
    ]

    for key in cli_overridable_keys:
        if key in args_dict and args_dict[key] is not None:
            result[key] = args_dict[key]

    return result


def apply_config_to_args(config: Dict[str, Any], args):
    """Apply configuration values to argparse namespace.

    This modifies the args namespace in place, setting values from the config
    only if the arg was not explicitly set via CLI.

    Args:
        config: Configuration dictionary
        args: argparse Namespace to update
    """
    args_dict = vars(args)

    for key, value in config.items():
        # Only set the value if the arg doesn't already have a non-None value
        # This ensures CLI args take precedence
        if key in args_dict and args_dict[key] is None:
            args_dict[key] = value


def get_effective_config(args) -> Dict[str, Any]:
    """Get the effective configuration by merging all layers including CLI args.

    This is the final configuration that would be used after all merging is complete.

    Args:
        args: argparse Namespace with CLI arguments

    Returns:
        Effective configuration dictionary
    """
    # Get the project config file path from args if present
    project_config_path = getattr(args, 'config_file', None)

    # Load layered config from files
    config = load_layered_config(project_config_path)

    # Merge in CLI args (highest priority)
    config = merge_cli_args(config, args)

    return config
