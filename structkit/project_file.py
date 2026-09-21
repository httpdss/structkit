"""Canonical and legacy project structure filenames.

The product was originally named STRUCT, so repositories commonly commit
``.struct.yaml``. The canonical name is now ``.structkit.yaml``. Commands that
default to the project structure file prefer the canonical name and fall back
to the legacy name when it is the only one present.
"""

import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

CANONICAL_PROJECT_STRUCT_FILE = ".structkit.yaml"
LEGACY_PROJECT_STRUCT_FILE = ".struct.yaml"
PROJECT_STRUCT_FILES = (
    CANONICAL_PROJECT_STRUCT_FILE,
    LEGACY_PROJECT_STRUCT_FILE,
)


def strip_file_scheme(path: str) -> Tuple[str, bool]:
    """Return (local_path, had_file_scheme) for a structure path."""
    if path.startswith("file://"):
        return path[7:], True
    return path, False


def is_default_project_struct_path(path: Optional[str]) -> bool:
    """Return True when path is omitted or names a default project file."""
    if not path:
        return True
    local_path, _ = strip_file_scheme(path)
    return os.path.basename(local_path) in PROJECT_STRUCT_FILES


def find_existing_project_struct_file(directory: str = ".") -> Optional[str]:
    """Return the existing default project file in directory, if any.

    Prefers ``.structkit.yaml`` over the legacy ``.struct.yaml``.
    """
    canonical = os.path.join(directory, CANONICAL_PROJECT_STRUCT_FILE)
    if os.path.isfile(canonical):
        return canonical

    legacy = os.path.join(directory, LEGACY_PROJECT_STRUCT_FILE)
    if os.path.isfile(legacy):
        return legacy

    return None


def resolve_project_struct_file(
    explicit_path: Optional[str] = None,
    directory: str = ".",
) -> str:
    """Resolve which project structure file a command should use.

    Non-default paths (named structures, custom YAML files) are returned
    unchanged. Default names prefer ``.structkit.yaml`` and fall back to
    ``.struct.yaml`` when the canonical file is missing.

    If neither default file exists, the canonical name is returned so error
    messages mention ``.structkit.yaml``.
    """
    if explicit_path and not is_default_project_struct_path(explicit_path):
        return explicit_path

    file_scheme = False
    search_dir = directory
    if explicit_path:
        local_path, file_scheme = strip_file_scheme(explicit_path)
        parent = os.path.dirname(local_path)
        if parent:
            search_dir = parent
            existing_path = local_path
        else:
            existing_path = os.path.join(directory, os.path.basename(local_path))
        if os.path.isfile(existing_path):
            return explicit_path

    canonical = os.path.normpath(os.path.join(search_dir, CANONICAL_PROJECT_STRUCT_FILE))
    legacy = os.path.normpath(os.path.join(search_dir, LEGACY_PROJECT_STRUCT_FILE))

    if os.path.isfile(canonical):
        if os.path.isfile(legacy):
            logger.info(
                "Both %s and %s exist; using %s. Rename or remove %s to avoid ambiguity.",
                CANONICAL_PROJECT_STRUCT_FILE,
                LEGACY_PROJECT_STRUCT_FILE,
                CANONICAL_PROJECT_STRUCT_FILE,
                LEGACY_PROJECT_STRUCT_FILE,
            )
        chosen = canonical
    elif os.path.isfile(legacy):
        logger.info(
            "Using legacy %s; prefer renaming it to %s.",
            LEGACY_PROJECT_STRUCT_FILE,
            CANONICAL_PROJECT_STRUCT_FILE,
        )
        chosen = legacy
    else:
        chosen = canonical

    if file_scheme:
        return f"file://{chosen}"
    if explicit_path and os.path.dirname(explicit_path) in ("", "."):
        # Keep a bare filename when the caller passed one (argparse default).
        return os.path.basename(chosen)
    if explicit_path is None and search_dir in ("", "."):
        return os.path.basename(chosen)
    return chosen
