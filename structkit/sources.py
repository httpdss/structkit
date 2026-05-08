"""Utilities for managing named StructKit structure sources."""

import json
import os
from pathlib import Path


CONFIG_ENV_VAR = "STRUCTKIT_SOURCES_CONFIG"
DEFAULT_CONFIG_PATH = Path.home() / ".config" / "structkit" / "sources.json"


class SourceConfigError(ValueError):
    """Raised when source configuration is invalid."""


def get_sources_config_path():
    """Return the user-level source config path.

    STRUCTKIT_SOURCES_CONFIG is primarily useful for tests and automation. Normal
    users get a platform-neutral file under ~/.config/structkit/sources.json.
    """
    configured_path = os.getenv(CONFIG_ENV_VAR)
    if configured_path:
        return Path(configured_path).expanduser()
    return DEFAULT_CONFIG_PATH


def normalize_source_path(path_or_url):
    """Normalize a local source path for storage."""
    if "://" in path_or_url:
        raise SourceConfigError("Only local filesystem source paths are supported right now")
    return str(Path(path_or_url).expanduser().resolve())


def read_sources(config_path=None):
    """Read source mappings from disk.

    Missing config files are treated as an empty mapping for first-run usage.
    """
    path = Path(config_path).expanduser() if config_path else get_sources_config_path()
    if not path.exists():
        return {}
    with open(path, "r") as f:
        data = json.load(f)
    if isinstance(data, dict) and isinstance(data.get("sources"), dict):
        return data["sources"]
    if isinstance(data, dict):
        return data
    raise SourceConfigError("Source config must contain a JSON object")


def write_sources(sources, config_path=None):
    """Write source mappings to disk."""
    path = Path(config_path).expanduser() if config_path else get_sources_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump({"sources": sources}, f, indent=2, sort_keys=True)
        f.write("\n")


def add_source(name, path_or_url, config_path=None):
    """Add or replace a named local source."""
    validate_source_name(name)
    normalized_path = normalize_source_path(path_or_url)
    if not os.path.isdir(normalized_path):
        raise SourceConfigError(f"Source path does not exist or is not a directory: {normalized_path}")
    sources = read_sources(config_path)
    sources[name] = normalized_path
    write_sources(sources, config_path)
    return normalized_path


def remove_source(name, config_path=None):
    """Remove a named source and return its path."""
    sources = read_sources(config_path)
    if name not in sources:
        raise SourceConfigError(f"Unknown source: {name}")
    removed_path = sources.pop(name)
    write_sources(sources, config_path)
    return removed_path


def get_source_path(name, config_path=None):
    """Return the configured path for a named source."""
    sources = read_sources(config_path)
    if name not in sources:
        raise SourceConfigError(f"Unknown source: {name}")
    return sources[name]


def validate_source(name, config_path=None):
    """Validate that a named source points to an existing directory."""
    source_path = get_source_path(name, config_path)
    if not os.path.isdir(source_path):
        raise SourceConfigError(f"Source path does not exist or is not a directory: {source_path}")
    return source_path


def validate_source_name(name):
    """Validate a source name used on the command line and in config."""
    if not name or name in {".", ".."}:
        raise SourceConfigError("Source name cannot be empty, '.' or '..'")
    if "/" in name or "\\" in name:
        raise SourceConfigError("Source name cannot contain path separators")


def split_source_prefix(structure_definition, config_path=None):
    """Split source-prefixed definitions like 'company/project/python'.

    Returns (source_name, remaining_definition, source_path) when the first path
    segment is a configured source name. Otherwise returns (None,
    structure_definition, None).
    """
    if structure_definition.startswith(("file://", "/", "./", "../")):
        return None, structure_definition, None
    if "/" not in structure_definition:
        return None, structure_definition, None
    source_name, rest = structure_definition.split("/", 1)
    sources = read_sources(config_path)
    if source_name in sources:
        return source_name, rest, validate_source(source_name, config_path)
    return None, structure_definition, None


def resolve_structures_path(args, structure_definition=None):
    """Resolve the effective structures path for commands.

    Precedence is:
    1. --structures-path or STRUCTKIT_STRUCTURES_PATH (already present on args)
    2. --source NAME
    3. source-prefixed structure names, for example company/project/python
    4. bundled contrib structures
    """
    if getattr(args, "structures_path", None):
        return args.structures_path, structure_definition

    source_name = getattr(args, "source", None)
    if source_name:
        return validate_source(source_name), structure_definition

    if structure_definition:
        _, stripped_definition, source_path = split_source_prefix(structure_definition)
        if source_path:
            return source_path, stripped_definition

    return None, structure_definition
