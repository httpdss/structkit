import argparse
import os
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

from structkit.commands.generate import GenerateCommand
from structkit.commands.list import ListCommand
from structkit.commands.sources import SourcesCommand
from structkit.mcp_server import StructMCPServer
from structkit.sources import (
    add_source,
    normalize_source_path,
    parse_remote_source,
    read_sources,
    resolve_source_path,
    resolve_structures_path,
)


def test_sources_config_read_write_and_validate(monkeypatch, tmp_path):
    config_path = tmp_path / "sources.yaml"
    source_dir = tmp_path / "templates"
    source_dir.mkdir()

    add_source("company", str(source_dir), str(config_path))

    assert read_sources(str(config_path)) == {"company": str(source_dir.resolve())}


def test_sources_command_add_list_show_validate_remove(capsys, tmp_path):
    parser = argparse.ArgumentParser()
    command = SourcesCommand(parser)
    config_path = tmp_path / "sources.yaml"
    source_dir = tmp_path / "templates"
    source_dir.mkdir()

    args = parser.parse_args(["--config-path", str(config_path), "add", "company", str(source_dir)])
    command.execute(args)
    assert "Added source 'company'" in capsys.readouterr().out

    args = parser.parse_args(["--config-path", str(config_path), "list"])
    command.execute(args)
    assert "company" in capsys.readouterr().out

    args = parser.parse_args(["--config-path", str(config_path), "show", "company"])
    command.execute(args)
    assert str(source_dir.resolve()) in capsys.readouterr().out

    args = parser.parse_args(["--config-path", str(config_path), "validate", "company"])
    command.execute(args)
    assert "is valid" in capsys.readouterr().out

    args = parser.parse_args(["--config-path", str(config_path), "remove", "company"])
    command.execute(args)
    assert "Removed source 'company'" in capsys.readouterr().out
    assert read_sources(str(config_path)) == {}


def test_sources_command_rejects_invalid_path(tmp_path):
    parser = argparse.ArgumentParser()
    command = SourcesCommand(parser)
    args = parser.parse_args([
        "--config-path",
        str(tmp_path / "sources.yaml"),
        "add",
        "missing",
        str(tmp_path / "missing"),
    ])

    with pytest.raises(SystemExit):
        command.execute(args)


def test_resolve_source_precedence(monkeypatch, tmp_path):
    config_path = tmp_path / "sources.yaml"
    source_dir = tmp_path / "templates"
    source_dir.mkdir()
    add_source("company", str(source_dir), str(config_path))
    monkeypatch.setenv("STRUCTKIT_SOURCES_CONFIG", str(config_path))

    resolved, definition = resolve_structures_path(None, None, "company/project/python")
    assert resolved == str(source_dir.resolve())
    assert definition == "project/python"

    resolved, definition = resolve_structures_path("/cli/path", "company", "company/project/python")
    assert resolved == "/cli/path"
    assert definition == "company/project/python"


def test_generate_uses_named_source_prefix(monkeypatch, tmp_path):
    config_path = tmp_path / "sources.yaml"
    source_dir = tmp_path / "templates"
    source_dir.mkdir()
    (source_dir / "demo.yaml").write_text("files: []\n")
    add_source("company", str(source_dir), str(config_path))
    monkeypatch.setenv("STRUCTKIT_SOURCES_CONFIG", str(config_path))

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)
    args = parser.parse_args(["company/demo", str(tmp_path / "out")])
    command.execute(args)

    assert args.structure_definition == "demo"
    assert args.structures_path == str(source_dir.resolve())


def test_list_uses_named_source(monkeypatch, capsys, tmp_path):
    config_path = tmp_path / "sources.yaml"
    source_dir = tmp_path / "templates"
    source_dir.mkdir()
    (source_dir / "demo.yaml").write_text("files: []\n")
    add_source("company", str(source_dir), str(config_path))
    monkeypatch.setenv("STRUCTKIT_SOURCES_CONFIG", str(config_path))

    parser = argparse.ArgumentParser()
    command = ListCommand(parser)
    args = parser.parse_args(["--source", "company", "--names-only"])
    command.execute(args)

    assert "demo" in capsys.readouterr().out


def _make_git_structures_repo(path: Path) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, stdout=subprocess.PIPE)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "demo.yaml").write_text("files:\n  - README.md:\n      content: remote demo\n")
    subprocess.run(["git", "add", "demo.yaml"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "add demo"], cwd=path, check=True, stdout=subprocess.PIPE)


def test_github_shorthand_sources_normalize_to_github_scheme(tmp_path):
    assert normalize_source_path("httpdss/structkit-templates") == "github://httpdss/structkit-templates"
    assert normalize_source_path("httpdss/structkit-templates@v1/structures") == (
        "github://httpdss/structkit-templates@v1/structures"
    )

    web_url = parse_remote_source("https://github.com/httpdss/structkit-templates/tree/v1/structures")
    assert web_url is not None
    assert web_url.git_url == "https://github.com/httpdss/structkit-templates.git"
    assert web_url.ref == "v1"
    assert web_url.subdir == "structures"

    local_dir = tmp_path / "owner" / "repo"
    local_dir.mkdir(parents=True)
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        assert normalize_source_path("owner/repo") == str(local_dir.resolve())
    finally:
        os.chdir(cwd)


def test_git_backed_source_resolves_to_cache_and_generates(monkeypatch, tmp_path):
    config_path = tmp_path / "sources.yaml"
    cache_dir = tmp_path / "cache"
    remote_repo = tmp_path / "remote-structures"
    _make_git_structures_repo(remote_repo)
    monkeypatch.setenv("STRUCTKIT_SOURCES_CACHE", str(cache_dir))
    monkeypatch.setenv("STRUCTKIT_SOURCES_CONFIG", str(config_path))

    add_source("company", remote_repo.as_uri(), str(config_path))
    stored = read_sources(str(config_path))["company"]
    assert stored == remote_repo.as_uri()

    resolved = resolve_source_path("company", str(config_path))
    assert resolved is not None
    assert Path(resolved, "demo.yaml").exists()
    assert str(cache_dir) in resolved

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)
    out_dir = tmp_path / "out"
    args = parser.parse_args(["company/demo", str(out_dir)])
    command.execute(args)

    assert args.structure_definition == "demo"
    assert args.structures_path == resolved
    assert (out_dir / "README.md").read_text().strip() == "remote demo"


def test_mcp_manage_sources(tmp_path):
    server = StructMCPServer()
    config_path = str(tmp_path / "sources.yaml")
    source_dir = tmp_path / "templates"
    source_dir.mkdir()

    added = server._manage_sources_logic("add", "company", str(source_dir), config_path)
    assert "Added source 'company'" in added

    listed = server._manage_sources_logic("list", config_path=config_path)
    assert "company" in listed

    validated = server._manage_sources_logic("validate", "company", config_path=config_path)
    assert "is valid" in validated

    removed = server._manage_sources_logic("remove", "company", config_path=config_path)
    assert "Removed source 'company'" in removed
