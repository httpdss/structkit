import argparse
import json
import os

import yaml

from structkit.commands.explain import ExplainCommand
from structkit.main import get_parser
from structkit.mcp_server import StructMCPServer


def write_yaml(path, data):
    path.write_text(yaml.safe_dump(data))


def test_explain_collects_nested_remote_hooks_vars_and_json(tmp_path):
    structures_path = tmp_path / "structures"
    structures_path.mkdir()
    base_path = tmp_path / "out"
    parent_path = tmp_path / "parent.yaml"
    child_path = structures_path / "child.yaml"

    write_yaml(child_path, {
        "variables": [
            {"module_name": {"type": "string", "default": "child_default"}},
        ],
        "files": [
            {"{{@ module_name @}}.txt": {"file": "https://example.com/template.txt"}},
        ],
    })
    write_yaml(parent_path, {
        "variables": [
            {"project_name": {"type": "string", "default": "demo"}},
        ],
        "pre_hooks": ["touch should-not-run-pre"],
        "post_hooks": ["touch should-not-run-post"],
        "files": [
            {"README.md": {"content": "# {{@ project_name @}}"}},
        ],
        "folders": [
            {"modules": {"struct": "child", "with": {"module_name": "{{@ project_name @}}-module"}}},
        ],
    })

    command = ExplainCommand(argparse.ArgumentParser())
    explanation = command.explain(
        str(parent_path),
        str(base_path),
        structures_path=str(structures_path),
        vars_str="project_name=acme",
    )

    assert explanation["creates_files"] is False
    assert explanation["executes_hooks"] is False
    assert not base_path.exists()
    assert explanation["hooks"]["pre"][0]["command"] == "touch should-not-run-pre"
    assert explanation["hooks"]["post"][0]["command"] == "touch should-not-run-post"
    assert explanation["variables"][0]["name"] == "project_name"
    assert explanation["variables"][0]["resolved_value"] == "acme"
    assert explanation["folders"][0]["path"] == os.path.join(str(base_path), "modules")
    assert explanation["nested_structures"][0]["structure"] == "child"
    assert explanation["nested_structures"][0]["vars"] == {"module_name": "acme-module"}
    assert explanation["remote_files"] == [{
        "structure": "child",
        "file": "https://example.com/template.txt",
        "path": os.path.join(str(base_path), "modules", "acme-module.txt"),
    }]

    rendered = command.format_text(explanation)
    assert "Safety: no files or folders will be created" in rendered
    assert "README.md action=create" in rendered
    assert "https://example.com/template.txt" in rendered


def test_explain_reports_existing_file_conflict_strategy(tmp_path):
    structure_path = tmp_path / "structure.yaml"
    base_path = tmp_path / "out"
    base_path.mkdir()
    (base_path / "README.md").write_text("old")
    write_yaml(structure_path, {"files": [{"README.md": {"content": "new"}}]})

    command = ExplainCommand(argparse.ArgumentParser())
    explanation = command.explain(str(structure_path), str(base_path), file_strategy="skip")

    assert explanation["files"][0]["exists"] is True
    assert explanation["files"][0]["conflict_action"] == "skip existing file"
    assert (base_path / "README.md").read_text() == "old"


def test_explain_command_is_registered_and_outputs_json(tmp_path, capsys):
    structure_path = tmp_path / "structure.yaml"
    write_yaml(structure_path, {"files": [{"README.md": {"content": "hello"}}]})

    parser = get_parser()
    args = parser.parse_args(["explain", str(structure_path), str(tmp_path / "out"), "--json"])
    args.func(args)
    data = json.loads(capsys.readouterr().out)

    assert data["structure"] == str(structure_path)
    assert data["files"][0]["name"] == "README.md"


def test_mcp_explain_structure_logic_and_tool_registration(tmp_path):
    structure_path = tmp_path / "structure.yaml"
    write_yaml(structure_path, {"files": [{"app.py": {"content": "print('hi')"}}]})

    server = StructMCPServer()
    tool_names = [tool.name for tool in __import__('asyncio').run(server.app.list_tools())]
    assert "explain_structure" in tool_names

    json_text = server._explain_structure_logic(str(structure_path), str(tmp_path / "out"), output="json")
    data = json.loads(json_text)
    assert data["files"][0]["path"] == os.path.join(str(tmp_path / "out"), "app.py")

    text = server._explain_structure_logic(str(structure_path), str(tmp_path / "out"))
    assert "Structure explanation" in text
