"""Utilities for managing named StructKit structure sources."""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import yaml


CONFIG_ENV_VAR = "STRUCTKIT_SOURCES_CONFIG"
CONFIG_DIR_ENV_VAR = "XDG_CONFIG_HOME"
CACHE_ENV_VAR = "STRUCTKIT_SOURCES_CACHE"
CACHE_DIR_ENV_VAR = "XDG_CACHE_HOME"


class SourceError(ValueError):
    """Raised when source configuration is invalid or cannot be resolved."""


@dataclass(frozen=True)
class RemoteSource:
    """A git-backed source normalized for local cache resolution."""

    git_url: str
    ref: Optional[str] = None
    subdir: str = ""


def get_sources_config_path() -> Path:
    """Return the user-level StructKit sources config path."""
    override = os.getenv(CONFIG_ENV_VAR)
    if override:
        return Path(override).expanduser()

    config_home = os.getenv(CONFIG_DIR_ENV_VAR)
    if config_home:
        return Path(config_home).expanduser() / "structkit" / "sources.yaml"

    return Path.home() / ".config" / "structkit" / "sources.yaml"


def get_sources_cache_dir() -> Path:
    """Return the cache directory used for git-backed sources."""
    override = os.getenv(CACHE_ENV_VAR)
    if override:
        return Path(override).expanduser()

    cache_home = os.getenv(CACHE_DIR_ENV_VAR)
    if cache_home:
        return Path(cache_home).expanduser() / "structkit" / "sources"

    return Path.home() / ".cache" / "structkit" / "sources"


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
            value = value.get("path") or value.get("url")
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


def is_github_shorthand(path_or_url: str) -> bool:
    """Return true for owner/repo shorthand values that are not local paths."""
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?(?:@[^/]+)?(?:/.+)?", path_or_url))


def is_remote_source(path_or_url: str) -> bool:
    path_without_query = path_or_url.split("?", 1)[0]
    if path_or_url.startswith("git@"):
        return True
    parsed = urlparse(path_or_url)
    if parsed.scheme in {"http", "https", "git", "ssh", "github", "file"}:
        return True
    # Preserve existing relative local-directory behavior: only treat owner/repo
    # shorthand as GitHub when that path is not present on disk.
    if is_github_shorthand(path_without_query) and not Path(path_without_query).expanduser().exists():
        return True
    return False


def _split_ref_and_subdir(value: str, explicit_ref: Optional[str] = None) -> Tuple[str, Optional[str], str]:
    """Split 'repo@ref/subdir' or 'repo/subdir' into repo, ref, subdir."""
    first, sep, rest = value.partition("/")
    repo_part = first
    subdir = rest if sep else ""
    if "@" in repo_part:
        repo, ref = repo_part.rsplit("@", 1)
    else:
        repo, ref = repo_part, None
    if explicit_ref:
        ref = explicit_ref
    return repo, ref, subdir.strip("/")


def parse_remote_source(path_or_url: str) -> Optional[RemoteSource]:
    """Parse supported git/GitHub source forms.

    Supported forms:
    - github://owner/repo
    - github://owner/repo@ref
    - github://owner/repo@ref/path/to/structures
    - owner/repo or owner/repo@ref shorthand
    - https://github.com/owner/repo(.git)
    - git@github.com:owner/repo.git
    - file:///path/to/repo for local git repositories used as remotes
    """
    if not is_remote_source(path_or_url):
        return None

    parsed = urlparse(path_or_url)
    query_ref = parse_qs(parsed.query).get("ref", [None])[0]
    path_without_query = path_or_url.split("?", 1)[0]

    if is_github_shorthand(path_without_query):
        owner, rest = path_without_query.split("/", 1)
        repo, ref, subdir = _split_ref_and_subdir(rest, query_ref)
        repo = repo[:-4] if repo.endswith(".git") else repo
        return RemoteSource(f"https://github.com/{owner}/{repo}.git", ref, subdir)

    if path_or_url.startswith("git@"):
        return RemoteSource(path_or_url)

    if parsed.scheme == "github":
        owner = parsed.netloc
        repo_path = parsed.path.lstrip("/")
        if not owner or not repo_path:
            raise SourceError("github sources must use github://owner/repo")
        repo, ref, subdir = _split_ref_and_subdir(repo_path, query_ref)
        repo = repo[:-4] if repo.endswith(".git") else repo
        return RemoteSource(f"https://github.com/{owner}/{repo}.git", ref, subdir)

    if parsed.scheme in {"http", "https"} and parsed.netloc.lower() == "github.com":
        parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(parts) < 2:
            raise SourceError("GitHub HTTPS sources must use https://github.com/owner/repo")
        owner, repo = parts[0], parts[1]
        ref = None
        subdir = ""
        if len(parts) >= 4 and parts[2] in {"tree", "blob"}:
            ref = parts[3]
            subdir = "/".join(parts[4:])
        elif len(parts) > 2:
            subdir = "/".join(parts[2:])
        if query_ref:
            ref = query_ref
        if repo.endswith(".git"):
            repo = repo[:-4]
            subdir = ""
        return RemoteSource(f"https://github.com/{owner}/{repo}.git", ref, subdir)

    if parsed.scheme in {"http", "https", "git", "ssh", "file"}:
        return RemoteSource(path_or_url)

    return None


def normalize_source_path(path_or_url: str) -> str:
    """Normalize a local source path while preserving supported remote source specs."""
    remote = parse_remote_source(path_or_url)
    if remote:
        if remote.git_url.startswith("https://github.com/"):
            owner_repo = remote.git_url.removeprefix("https://github.com/").removesuffix(".git")
            subdir = f"/{remote.subdir}" if remote.subdir else ""
            if remote.ref and "/" in remote.ref:
                return f"github://{owner_repo}{subdir}?ref={remote.ref}"
            suffix = f"@{remote.ref}" if remote.ref else ""
            return f"github://{owner_repo}{suffix}{subdir}"
        return path_or_url
    return str(Path(path_or_url).expanduser().resolve())


def _source_cache_path(remote: RemoteSource) -> Path:
    cache_identity = f"{remote.git_url}@{remote.ref or 'HEAD'}"
    key = hashlib.sha256(cache_identity.encode("utf-8")).hexdigest()[:16]
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", cache_identity).strip("-")[-64:]
    return get_sources_cache_dir() / f"{safe}-{key}"


def _run_git(args: list[str], cwd: Optional[Path] = None) -> None:
    try:
        subprocess.run(
            ["git", *args],
            cwd=str(cwd) if cwd else None,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except FileNotFoundError:
        raise SourceError("git is required for remote sources but was not found on PATH") from None
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise SourceError(f"git {' '.join(args)} failed: {detail}") from None


def _git_succeeds(args: list[str], cwd: Path) -> bool:
    try:
        subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False


def _checkout_remote_ref(remote: RemoteSource, cache_path: Path) -> None:
    _run_git(["fetch", "--prune", "--tags", "origin"], cwd=cache_path)
    if not remote.ref:
        return

    if _git_succeeds(["show-ref", "--verify", f"refs/remotes/origin/{remote.ref}"], cwd=cache_path):
        _run_git(["checkout", "-B", remote.ref, f"origin/{remote.ref}"], cwd=cache_path)
    else:
        _run_git(["checkout", "--detach", remote.ref], cwd=cache_path)


def ensure_remote_repo(path_or_url: str) -> str:
    """Clone/fetch a remote source and return the checked-out repository root."""
    remote = parse_remote_source(path_or_url)
    if not remote:
        return str(Path(path_or_url).expanduser().resolve())

    cache_path = _source_cache_path(remote)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if not (cache_path / ".git").exists():
        if cache_path.exists():
            shutil.rmtree(cache_path)
        _run_git(["clone", remote.git_url, str(cache_path)])

    _checkout_remote_ref(remote, cache_path)
    return str(cache_path)


def ensure_remote_source(path_or_url: str) -> str:
    """Clone/fetch a remote source and return the local structures path."""
    remote = parse_remote_source(path_or_url)
    if not remote:
        return str(Path(path_or_url).expanduser().resolve())

    cache_path = Path(ensure_remote_repo(path_or_url))

    structures_path = cache_path / remote.subdir if remote.subdir else cache_path
    if not structures_path.exists():
        raise SourceError(f"remote source subdirectory does not exist: {remote.subdir or '.'}")
    if not structures_path.is_dir():
        raise SourceError(f"remote source subdirectory is not a directory: {remote.subdir}")
    return str(structures_path)


def validate_source_path(path_or_url: str) -> Tuple[bool, str]:
    """Validate that a source points at a usable local directory or git-backed source."""
    remote = parse_remote_source(path_or_url)
    if remote:
        try:
            local_path = ensure_remote_source(path_or_url)
        except SourceError as exc:
            return False, str(exc)
        return True, f"valid remote source: {path_or_url} -> {local_path}"

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
    return ensure_remote_source(sources[source]) if is_remote_source(sources[source]) else sources[source]


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
