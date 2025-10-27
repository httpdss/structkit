import builtins
import os
import subprocess
import textwrap
import types
import yaml
import pytest

from structkit import utils


def test_read_config_file(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text(textwrap.dedent(
        """
        a: 1
        b: two
        nested:
          x: y
        """
    ))
    data = utils.read_config_file(str(cfg))
    assert data == {"a": 1, "b": "two", "nested": {"x": "y"}}


def test_merge_configs_prefers_args_and_fills_missing():
    class Args:
        def __init__(self):
            self.a = None
            self.b = "cli"
            self.c = None
    args = Args()
    merged = utils.merge_configs({"a": 1, "b": "file", "c": 3}, args)
    assert merged["a"] == 1  # filled from file because arg is None
    assert merged["b"] == "cli"  # arg wins because it is not None
    assert merged["c"] == 3


def test_get_current_repo_https(monkeypatch):
    def fake_check_output(cmd, text):
        return "https://github.com/owner/repo.git\n"
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert utils.get_current_repo() == "owner/repo"


def test_get_current_repo_ssh(monkeypatch):
    def fake_check_output(cmd, text):
        return "git@github.com:owner/repo.git\n"
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert utils.get_current_repo() == "owner/repo"


def test_get_current_repo_not_github(monkeypatch):
    # Current behavior: any git@host format returns owner/repo regardless of host
    def fake_check_output(cmd, text):
        return "git@example.com:owner/repo.git\n"
    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    assert utils.get_current_repo() == "owner/repo"


def test_get_current_repo_not_git(monkeypatch):
    def raise_called(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["git", "config"])  # simulate no git
    monkeypatch.setattr(subprocess, "check_output", raise_called)
    assert utils.get_current_repo() == "Error: Not a Git repository or no remote URL set"
