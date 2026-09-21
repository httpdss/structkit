import argparse

from structkit.commands.generate import GenerateCommand
from structkit.commands.init import InitCommand
from structkit.project_file import (
    CANONICAL_PROJECT_STRUCT_FILE,
    LEGACY_PROJECT_STRUCT_FILE,
    find_existing_project_struct_file,
    is_default_project_struct_path,
    resolve_project_struct_file,
    strip_file_scheme,
)


def test_strip_file_scheme():
    assert strip_file_scheme("file://.structkit.yaml") == (".structkit.yaml", True)
    assert strip_file_scheme(".struct.yaml") == (".struct.yaml", False)


def test_is_default_project_struct_path():
    assert is_default_project_struct_path(None) is True
    assert is_default_project_struct_path("") is True
    assert is_default_project_struct_path(".structkit.yaml") is True
    assert is_default_project_struct_path(".struct.yaml") is True
    assert is_default_project_struct_path("file://.struct.yaml") is True
    assert is_default_project_struct_path("examples/app/.structkit.yaml") is True
    assert is_default_project_struct_path("project/python") is False
    assert is_default_project_struct_path("my-config.yaml") is False


def test_find_existing_prefers_canonical(tmp_path):
    (tmp_path / CANONICAL_PROJECT_STRUCT_FILE).write_text("files: []\n")
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text("files: []\n")

    found = find_existing_project_struct_file(str(tmp_path))

    assert found.endswith(CANONICAL_PROJECT_STRUCT_FILE)


def test_find_existing_falls_back_to_legacy(tmp_path):
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text("files: []\n")

    found = find_existing_project_struct_file(str(tmp_path))

    assert found.endswith(LEGACY_PROJECT_STRUCT_FILE)


def test_find_existing_returns_none_when_missing(tmp_path):
    assert find_existing_project_struct_file(str(tmp_path)) is None


def test_resolve_leaves_named_structures_unchanged():
    assert resolve_project_struct_file("project/python") == "project/python"
    assert resolve_project_struct_file("file://custom.yaml") == "file://custom.yaml"


def test_resolve_prefers_canonical_when_both_exist(tmp_path):
    (tmp_path / CANONICAL_PROJECT_STRUCT_FILE).write_text("canonical: true\n")
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text("legacy: true\n")

    resolved = resolve_project_struct_file(directory=str(tmp_path))

    assert resolved.endswith(CANONICAL_PROJECT_STRUCT_FILE)


def test_resolve_falls_back_to_legacy_default_name(tmp_path):
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text("legacy: true\n")

    resolved = resolve_project_struct_file(
        explicit_path=CANONICAL_PROJECT_STRUCT_FILE,
        directory=str(tmp_path),
    )

    assert resolved.endswith(LEGACY_PROJECT_STRUCT_FILE)


def test_resolve_keeps_explicit_legacy_file_when_it_exists(tmp_path):
    (tmp_path / CANONICAL_PROJECT_STRUCT_FILE).write_text("canonical: true\n")
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text("legacy: true\n")
    explicit = str(tmp_path / LEGACY_PROJECT_STRUCT_FILE)

    resolved = resolve_project_struct_file(explicit_path=explicit, directory=str(tmp_path))

    assert resolved == explicit


def test_resolve_rewrites_missing_legacy_path_to_canonical(tmp_path):
    (tmp_path / CANONICAL_PROJECT_STRUCT_FILE).write_text("canonical: true\n")
    explicit = str(tmp_path / LEGACY_PROJECT_STRUCT_FILE)

    resolved = resolve_project_struct_file(explicit_path=explicit, directory=str(tmp_path))

    assert resolved.endswith(CANONICAL_PROJECT_STRUCT_FILE)


def test_resolve_preserves_file_scheme_on_fallback(tmp_path):
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text("legacy: true\n")
    explicit = f"file://{tmp_path / CANONICAL_PROJECT_STRUCT_FILE}"

    resolved = resolve_project_struct_file(explicit_path=explicit, directory=str(tmp_path))

    assert resolved.startswith("file://")
    assert resolved.endswith(LEGACY_PROJECT_STRUCT_FILE)


def test_resolve_returns_canonical_when_neither_exists(tmp_path):
    resolved = resolve_project_struct_file(directory=str(tmp_path))
    assert resolved.endswith(CANONICAL_PROJECT_STRUCT_FILE)


def test_generate_uses_legacy_struct_yaml_when_canonical_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text(
        "files:\n  - hello.txt:\n      content: from-legacy\n"
    )
    out_dir = tmp_path / "out"
    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)
    args = parser.parse_args(["--non-interactive", CANONICAL_PROJECT_STRUCT_FILE, str(out_dir)])

    command.execute(args)

    assert (out_dir / "hello.txt").read_text().strip() == "from-legacy"


def test_generate_prefers_structkit_yaml_when_both_exist(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / LEGACY_PROJECT_STRUCT_FILE).write_text(
        "files:\n  - hello.txt:\n      content: from-legacy\n"
    )
    (tmp_path / CANONICAL_PROJECT_STRUCT_FILE).write_text(
        "files:\n  - hello.txt:\n      content: from-canonical\n"
    )
    out_dir = tmp_path / "out"
    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)
    args = parser.parse_args(["--non-interactive", CANONICAL_PROJECT_STRUCT_FILE, str(out_dir)])

    command.execute(args)

    assert (out_dir / "hello.txt").read_text().strip() == "from-canonical"


def test_init_skips_legacy_struct_yaml(tmp_path):
    parser = argparse.ArgumentParser()
    cmd = InitCommand(parser)
    target_dir = tmp_path / "proj"
    target_dir.mkdir()
    existing = target_dir / LEGACY_PROJECT_STRUCT_FILE
    existing.write_text("files: []\n")

    args = parser.parse_args([str(target_dir)])
    printed = []

    def capture(message):
        printed.append(message)

    from unittest.mock import patch
    with patch("builtins.print", side_effect=capture):
        cmd.execute(args)

    assert existing.read_text() == "files: []\n"
    assert not (target_dir / CANONICAL_PROJECT_STRUCT_FILE).exists()
    output = "\n".join(printed)
    assert LEGACY_PROJECT_STRUCT_FILE in output
    assert CANONICAL_PROJECT_STRUCT_FILE in output
