"""Utilities for managing named StructKit structure sources."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import yaml


CONFIG_ENV_VAR = "STRUCTKIT_SOURCES_CONFIG"
CONFIG_DIR_ENV_VAR = "XDG_CONFIG_HOME"


class SourceError(ValueError):
    """Raised when source configuration is invalid or cannot be resolved."""


def get_sources_config_path() -> Path:
    """Return the user-level StructKit sources config path."""
    override = os.getenv(CONFIG_ENV_VAR)
    if override:
        return Path(override).expanduser()

    config_home = os.getenv(CONFIG_DIR_ENV_VAR)
    if config_home:
        return Path(config_home).expanduser() / "structkit" / "sources.yaml"

    return Path.home() / ".config" / "structkit" / "sources.yaml"


def read_sources(config_path: Optional[str] = None) -> Dict[str, str]:
    """Read configured sources from disk as a name-to-path mapping."""
    path = Path(config_path).expanduser() if config_path else get_sources_config_path()
    if not path.exists():
        return {}

    with open(path, "r") as f:
        data = yaml.safe_load(f) or {}

    sources = data.get("sources", data) if isinstance(data, dict) else {}
    if not isinstance(sources, dict):
        raise SourceError("sources config must contain a mapping of names to paths")

    result: Dict[str, str] = {}
    for name, value in sources.items():
        if isinstance(value, dict):
            value = value.get("path")
        if not isinstance(name, str) or not name:
            raise SourceError("source names must be non-empty strings")
        if not isinstance(value, str) or not value:
            raise SourceError(f"source '{name}' must have a non-empty path")
        result[name] = value
    return result


def write_sources(sources: Dict[str, str], config_path: Optional[str] = None) -> Path:
    """Write source configuration and return the path used."""
    path = Path(config_path).expanduser() if config_path else get_sources_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"sources": {name: {"path": value} for name, value in sorted(sources.items())}}
    with open(path, "w") as f:
        yaml.safe_dump(payload, f, sort_keys=True)
    return path


def is_remote_source(path_or_url: str) -> bool:
    parsed = urlparse(path_or_url)
    return parsed.scheme in {"http", "https", "git", "ssh"}


def normalize_source_path(path_or_url: str) -> str:
    """Normalize a local source path, preserving remote URLs for future support."""
    if is_remote_source(path_or_url):
        return path_or_url
    return str(Path(path_or_url).expanduser().resolve())


def validate_source_path(path_or_url: str) -> Tuple[bool, str]:
    """Validate that a source points at a usable local directory."""
    if is_remote_source(path_or_url):
        return False, "remote sources are not supported yet"

    path = Path(path_or_url).expanduser()
    if not path.exists():
        return False, f"path does not exist: {path}"
    if not path.is_dir():
        return False, f"path is not a directory: {path}"
    return True, f"valid local source: {path.resolve()}"


def add_source(name: str, path_or_url: str, config_path: Optional[str] = None) -> Path:
    sources = read_sources(config_path)
    ok, message = validate_source_path(path_or_url)
    if not ok:
        raise SourceError(message)
    sources[name] = normalize_source_path(path_or_url)
    return write_sources(sources, config_path)


def remove_source(name: str, config_path: Optional[str] = None) -> Path:
    sources = read_sources(config_path)
    if name not in sources:
        raise SourceError(f"source not found: {name}")
    del sources[name]
    return write_sources(sources, config_path)


def resolve_source_path(source: Optional[str], config_path: Optional[str] = None) -> Optional[str]:
    if not source:
        return None
    sources = read_sources(config_path)
    if source not in sources:
        raise SourceError(f"source not found: {source}")
    return sources[source]


def split_source_definition(structure_definition: str, config_path: Optional[str] = None) -> Tuple[Optional[str], str]:
    """Split '<source>/<structure>' when the first segment is a configured source."""
    if not structure_definition or structure_definition.startswith(("file://", "/")):
        return None, structure_definition
    first, sep, rest = structure_definition.partition("/")
    if not sep or not rest:
        return None, structure_definition
    sources = read_sources(config_path)
    if first in sources:
        return first, rest
    return None, structure_definition


def resolve_structures_path(
    structures_path: Optional[str],
    source: Optional[str],
    structure_definition: Optional[str] = None,
    config_path: Optional[str] = None,
) -> Tuple[Optional[str], Optional[str]]:
    """Resolve effective structures path and possibly rewritten structure name.

    Precedence is explicit --structures-path first, then --source or a
    '<source>/<structure>' prefix, then existing STRUCTKIT_STRUCTURES_PATH/default
    behavior handled by callers.
    """
    if structures_path:
        return structures_path, structure_definition

    selected_source = source
    rewritten = structure_definition
    if not selected_source and structure_definition:
        selected_source, rewritten = split_source_definition(structure_definition, config_path)

    if selected_source:
        return resolve_source_path(selected_source, config_path), rewritten
    return structures_path, rewritten
