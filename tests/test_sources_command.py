import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest

from structkit.commands.generate import GenerateCommand
from structkit.commands.list import ListCommand
from structkit.commands.sources import SourcesCommand
from structkit.sources import (
    SourceConfigError,
    add_source,
    get_source_path,
    read_sources,
    remove_source,
    resolve_structures_path,
    validate_source,
)


def test_source_config_read_write_add_show_remove(tmp_path):
    config_path = tmp_path / "sources.json"
    structures_dir = tmp_path / "templates"
    structures_dir.mkdir()

    added_path = add_source("company", str(structures_dir), config_path)

    assert added_path == str(structures_dir.resolve())
    assert read_sources(config_path) == {"company": str(structures_dir.resolve())}
    assert get_source_path("company", config_path) == str(structures_dir.resolve())
    assert validate_source("company", config_path) == str(structures_dir.resolve())
    assert remove_source("company", config_path) == str(structures_dir.resolve())
    assert read_sources(config_path) == {}


def test_add_source_rejects_invalid_local_path(tmp_path):
    with pytest.raises(SourceConfigError, match="not a directory"):
        add_source("missing", str(tmp_path / "missing"), tmp_path / "sources.json")


def test_add_source_rejects_remote_urls(tmp_path):
    with pytest.raises(SourceConfigError, match="Only local filesystem"):
        add_source("remote", "https://example.com/templates.git", tmp_path / "sources.json")


def test_missing_source_errors(tmp_path):
    config_path = tmp_path / "sources.json"
    config_path.write_text(json.dumps({"sources": {}}))

    with pytest.raises(SourceConfigError, match="Unknown source"):
        get_source_path("missing", config_path)


def test_resolve_structures_path_uses_structures_path_before_source(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    cli_dir = tmp_path / "cli"
    cli_dir.mkdir()
    config_path = tmp_path / "sources.json"
    add_source("company", str(source_dir), config_path)
    args = argparse.Namespace(structures_path=str(cli_dir), source="company")

    with patch.dict(os.environ, {"STRUCTKIT_SOURCES_CONFIG": str(config_path)}):
        path, structure = resolve_structures_path(args, "project/python")

    assert path == str(cli_dir)
    assert structure == "project/python"


def test_resolve_structures_path_uses_named_source(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    config_path = tmp_path / "sources.json"
    add_source("company", str(source_dir), config_path)
    args = argparse.Namespace(structures_path=None, source="company")

    with patch.dict(os.environ, {"STRUCTKIT_SOURCES_CONFIG": str(config_path)}):
        path, structure = resolve_structures_path(args, "project/python")

    assert path == str(source_dir.resolve())
    assert structure == "project/python"


def test_resolve_structures_path_uses_source_prefix(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    config_path = tmp_path / "sources.json"
    add_source("company", str(source_dir), config_path)
    args = argparse.Namespace(structures_path=None, source=None)

    with patch.dict(os.environ, {"STRUCTKIT_SOURCES_CONFIG": str(config_path)}):
        path, structure = resolve_structures_path(args, "company/project/python")

    assert path == str(source_dir.resolve())
    assert structure == "project/python"


def test_sources_command_list_add_show_validate_remove(tmp_path, capsys):
    config_path = tmp_path / "sources.json"
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    parser = argparse.ArgumentParser()
    SourcesCommand(parser)

    with patch.dict(os.environ, {"STRUCTKIT_SOURCES_CONFIG": str(config_path)}):
        args = parser.parse_args(["add", "company", str(source_dir)])
        args.func(args)
        assert "Added source 'company'" in capsys.readouterr().out

        args = parser.parse_args(["list"])
        args.func(args)
        assert "company" in capsys.readouterr().out

        args = parser.parse_args(["show", "company"])
        args.func(args)
        assert str(source_dir.resolve()) in capsys.readouterr().out

        args = parser.parse_args(["validate", "company"])
        args.func(args)
        assert "is valid" in capsys.readouterr().out

        args = parser.parse_args(["remove", "company"])
        args.func(args)
        assert "Removed source 'company'" in capsys.readouterr().out


def test_list_command_uses_named_source(tmp_path, capsys):
    config_path = tmp_path / "sources.json"
    source_dir = tmp_path / "source"
    (source_dir / "project").mkdir(parents=True)
    (source_dir / "project" / "python.yaml").write_text("files: []\n")
    add_source("company", str(source_dir), config_path)
    parser = argparse.ArgumentParser()
    ListCommand(parser)

    with patch.dict(os.environ, {"STRUCTKIT_SOURCES_CONFIG": str(config_path)}):
        args = parser.parse_args(["--source", "company", "--names-only"])
        args.func(args)

    assert "project/python" in capsys.readouterr().out


def test_generate_command_uses_source_prefix(tmp_path):
    config_path = tmp_path / "sources.json"
    source_dir = tmp_path / "source"
    (source_dir / "project").mkdir(parents=True)
    (source_dir / "project" / "python.yaml").write_text("files: []\n")
    output_dir = tmp_path / "output"
    add_source("company", str(source_dir), config_path)
    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)

    with patch.dict(os.environ, {"STRUCTKIT_SOURCES_CONFIG": str(config_path)}):
        args = parser.parse_args(["company/project/python", str(output_dir)])
        command.execute(args)

    assert args.structures_path == str(source_dir.resolve())
    assert args.structure_definition == "project/python"
