import argparse
import json

import pytest

from structkit.commands.graph import GraphCommand
from structkit.main import get_parser


def write_structure(base, name, folders=None):
    path = base / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["files: []\n"]
    if folders is not None:
        lines.append("folders:\n")
        for folder, struct_value in folders:
            lines.append(f"  - {folder}:\n")
            if isinstance(struct_value, list):
                lines.append("      struct:\n")
                for item in struct_value:
                    lines.append(f"        - {item}\n")
            else:
                lines.append(f"      struct: {struct_value}\n")
    path.write_text("".join(lines))
    return path


@pytest.fixture
def graph_command():
    return GraphCommand(argparse.ArgumentParser())


def test_graph_command_registered():
    parser = get_parser()
    args = parser.parse_args(['graph', 'project/python'])
    assert callable(args.func)
    assert args.structure_definition == 'project/python'
    assert args.format == 'text'


def test_graph_single_dependency(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('src', 'library')])
    write_structure(tmp_path, 'library')

    graph = graph_command.build_graph('app', str(tmp_path))

    assert graph['nodes'] == ['app', 'library']
    assert graph['edges'] == [{'from': 'app', 'to': 'library'}]
    assert graph['missing'] == []
    assert graph['cycles'] == []


def test_graph_multiple_dependencies(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('infra', ['terraform', 'kubernetes'])])
    write_structure(tmp_path, 'terraform')
    write_structure(tmp_path, 'kubernetes')

    graph = graph_command.build_graph('app', str(tmp_path))

    assert graph['edges'] == [
        {'from': 'app', 'to': 'kubernetes'},
        {'from': 'app', 'to': 'terraform'},
    ]


def test_graph_nested_dependencies(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('src', 'api')])
    write_structure(tmp_path, 'api', [('config', 'shared/config')])
    write_structure(tmp_path, 'shared/config')

    graph = graph_command.build_graph('app', str(tmp_path))

    assert {'from': 'app', 'to': 'api'} in graph['edges']
    assert {'from': 'api', 'to': 'shared/config'} in graph['edges']
    text = graph_command.format_text(graph)
    assert 'app' in text
    assert 'api' in text
    assert 'shared/config' in text


def test_graph_missing_dependency(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('src', 'missing-lib')])

    graph = graph_command.build_graph('app', str(tmp_path))

    assert graph['missing'] == [{'from': 'app', 'to': 'missing-lib'}]
    assert 'missing-lib (missing)' in graph_command.format_text(graph)


def test_graph_cycles(graph_command, tmp_path):
    write_structure(tmp_path, 'a', [('b-folder', 'b')])
    write_structure(tmp_path, 'b', [('a-folder', 'a')])

    graph = graph_command.build_graph('a', str(tmp_path))

    assert graph['cycles'] == [['a', 'b', 'a']]
    assert 'a -> b -> a' in graph_command.format_text(graph)


def test_graph_json_output(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('src', 'library')])
    write_structure(tmp_path, 'library')

    graph = graph_command.build_graph('app', str(tmp_path))
    payload = json.loads(graph_command.format_json(graph))

    assert payload['roots'] == ['app']
    assert payload['edges'] == [{'from': 'app', 'to': 'library'}]


def test_graph_mermaid_output(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('src', 'library')])
    write_structure(tmp_path, 'library')

    graph = graph_command.build_graph('app', str(tmp_path))
    mermaid = graph_command.format_mermaid(graph)

    assert mermaid.startswith('graph TD')
    assert 'n_app["app"] --> n_library["library"]' in mermaid
    assert 'classDef missing' in mermaid


def test_graph_all_includes_all_available_roots(graph_command, tmp_path):
    write_structure(tmp_path, 'app', [('src', 'library')])
    write_structure(tmp_path, 'library')
    write_structure(tmp_path, 'standalone')

    graph = graph_command.build_graph(structures_path=str(tmp_path), include_all=True)

    assert 'app' in graph['roots']
    assert 'library' in graph['roots']
    assert 'standalone' in graph['roots']
