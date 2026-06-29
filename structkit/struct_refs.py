"""Resolution helpers for nested StructKit structure references."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Mapping, Optional, Tuple

from structkit.sources import (
    SourceError,
    ensure_remote_repo,
    ensure_remote_source,
    is_remote_source,
    parse_remote_source,
    read_sources,
)


@dataclass
class SourceContext:
    """Named sources available while recursively generating structures."""

    sources: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_global(cls, config_path: Optional[str] = None) -> "SourceContext":
        return cls(dict(read_sources(config_path)))

    def merge_inline(self, inline_sources: Optional[Mapping[str, object]], *, allow_override: bool = False) -> "SourceContext":
        """Return a context extended with sources declared in a struct config.

        Top-level configs may override user-level global sources for portability.
        Nested configs may add new source names but cannot silently redefine names
        inherited from their parent generation context.
        """
        if not inline_sources:
            return SourceContext(dict(self.sources))
        if not isinstance(inline_sources, Mapping):
            raise SourceError("'sources' must be a mapping of names to paths or {url/path: ...} objects")

        merged = dict(self.sources)
        for name, value in inline_sources.items():
            if not isinstance(name, str) or not name:
                raise SourceError("source names must be non-empty strings")
            source_value = value
            if isinstance(value, Mapping):
                source_value = value.get("path") or value.get("url")
            if not isinstance(source_value, str) or not source_value:
                raise SourceError(f"source '{name}' must have a non-empty path or url")
            if not allow_override and name in merged and merged[name] != source_value:
                raise SourceError(
                    f"source '{name}' is already defined by the parent context; "
                    "use a different name to reference another version"
                )
            merged[name] = source_value
        return SourceContext(merged)


def _is_file_reference(structure_definition: str) -> bool:
    return (
        structure_definition.startswith("file://")
        or structure_definition.startswith("/")
        or structure_definition.endswith(".yaml")
    )


def _split_named_source(structure_definition: str, context: SourceContext) -> Tuple[Optional[str], str]:
    first, sep, rest = structure_definition.partition("/")
    if sep and rest and first in context.sources:
        return first, rest
    return None, structure_definition


def _direct_remote_struct_ref(structure_definition: str) -> Optional[Tuple[str, str]]:
    """Resolve a fully-qualified remote struct reference.

    The remote URL identifies a repository/ref plus a path that contains both the
    structures root and the structure name, for example:

      github://owner/repo@v1/structures/python/fastapi

    After checking out the remote ref, this finds the deepest split where the
    prefix is an existing directory and the suffix points at a YAML struct file.
    """
    remote = parse_remote_source(structure_definition)
    if not remote or not remote.subdir:
        return None

    repo_root = Path(ensure_remote_repo(structure_definition))
    parts = [part for part in remote.subdir.split("/") if part]
    if not parts:
        return None

    # Prefer the longest structure name under the shallowest valid structures
    # directory, so structures/python/fastapi -> structures + python/fastapi.
    for split_at in range(1, len(parts)):
        structures_path = repo_root / Path(*parts[:split_at])
        struct_name = "/".join(parts[split_at:])
        if structures_path.is_dir() and (structures_path / f"{struct_name}.yaml").is_file():
            return str(structures_path), struct_name

    # Also support fully-qualified references that include the .yaml suffix.
    full_path = repo_root / remote.subdir
    if full_path.is_file() and full_path.suffix in {".yaml", ".yml"}:
        return str(full_path.parent), full_path.stem

    raise SourceError(
        f"remote struct reference does not point to a YAML struct: {structure_definition}"
    )


def resolve_struct_reference(
    structure_definition: str,
    current_structures_path: Optional[str],
    context: Optional[SourceContext] = None,
) -> Tuple[Optional[str], str]:
    """Resolve one nested struct reference to a structures path and struct name."""
    if not isinstance(structure_definition, str) or not structure_definition:
        raise SourceError("struct references must be non-empty strings")

    if _is_file_reference(structure_definition):
        return current_structures_path, structure_definition

    context = context or SourceContext.from_global()

    source_name, rewritten = _split_named_source(structure_definition, context)
    if source_name:
        source_value = context.sources[source_name]
        source_path = ensure_remote_source(source_value) if is_remote_source(source_value) else str(Path(source_value).expanduser().resolve())
        return source_path, rewritten

    # Treat only explicit URL/git forms as fully-qualified remote struct refs.
    # Plain values like "category/structure" must remain normal local/built-in
    # struct names instead of being mistaken for GitHub owner/repo shorthand.
    if "://" in structure_definition or structure_definition.startswith("git@"):
        direct = _direct_remote_struct_ref(structure_definition)
        if direct:
            return direct

    return current_structures_path, structure_definition
