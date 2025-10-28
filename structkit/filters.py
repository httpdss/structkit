import os
import re
import json
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

import yaml
from github import Github
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=100, ttl=600)


@cached(cache)
def get_latest_release(repo_name):
    token = os.getenv('GITHUB_TOKEN')

    # Use the token if available, otherwise proceed without authentication
    if token:
      g = Github(token)
    else:
      g = Github()

    try:
      # Get the repository object
      repo = g.get_repo(repo_name)
      # Get the latest release
      latest_release = repo.get_latest_release()
      return latest_release.tag_name
    except Exception:
      # If an error occurs, return the default branch name
      try:
        default_branch = repo.default_branch
        return default_branch
      except Exception as e:
        print(f"Error getting default branch: {e}")
        return "LATEST_RELEASE_ERROR"


@cached(cache)
def get_default_branch(repo_name):
    token = os.getenv('GITHUB_TOKEN')

    if token:
        g = Github(token)
    else:
        g = Github()

    try:
        repo = g.get_repo(repo_name)
        return repo.default_branch
    except Exception:
        return "DEFAULT_BRANCH_ERROR"


def slugify(value):
    # Convert to lowercase
    value = value.lower()
    # Replace spaces with hyphens
    value = re.sub(r'\s+', '-', value)
    # Remove any non-alphanumeric characters (except hyphens)
    value = re.sub(r'[^a-z0-9-]', '', value)
    return value

# -----------------------------
# Additional helpers/filters
# -----------------------------


def gen_uuid() -> str:
    return str(uuid4())


def now_iso() -> str:
    # UTC ISO8601 string
    return datetime.now(timezone.utc).isoformat()


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default)


def read_file(path: str, encoding: str = "utf-8") -> str:
    try:
        with open(path, "r", encoding=encoding) as f:
            return f.read()
    except Exception:
        return ""


def to_yaml(obj: Any) -> str:
    try:
        return yaml.safe_dump(obj, sort_keys=False)
    except Exception:
        return ""


def from_yaml(s: str) -> Any:
    try:
        return yaml.safe_load(s)
    except Exception:
        return None


def to_json(obj: Any, indent: int | None = None) -> str:
    try:
        return json.dumps(obj, indent=indent)
    except Exception:
        return ""


def from_json(s: str) -> Any:
    try:
        return json.loads(s)
    except Exception:
        return None
