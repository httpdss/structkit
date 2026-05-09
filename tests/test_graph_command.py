import argparse
import asyncio
import json
import os

import yaml

from structkit.commands.graph import GraphCommand
from structkit.mcp_server import StructMCPServer


def write_structure(base, name, folders=None):
    path = base / f"{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({'folders': folders or []}))
    return path


def build_command():
    parser = argparse.ArgumentParser()
    return GraphCommand(parser)


def test_graph_single_dependency(tmp_path):
    write_structure(tmp_path, 'app', [{'lib': {'struct': 'library'}}])
    write_structure(tmp_path, 'library')

    graph = build_command().build_graph('app', structures_path=str(tmp_path))

    assert graph['roots'] == ['app']
    assert {'from': 'app', 'to': 'library', 'folder': 'lib'} in graph['edges']
    assert graph['missing'] == []
    assert graph['cycles'] == []


def test_graph_multiple_dependencies(tmp_path):
    write_structure(tmp_path, 'app', [{'deps': {'struct': ['api', 'web']}}])
    write_structure(tmp_path, 'api')
    write_structure(tmp_path, 'web')

    graph = build_command().build_graph('app', structures_path=str(tmp_path))

    assert {'from': 'app', 'to': 'api', 'folder': 'deps'} in graph['edges']
    assert {'from': 'app', 'to': 'web', 'folder': 'deps'} in graph['edges']


def test_graph_nested_dependencies(tmp_path):
    write_structure(tmp_path, 'app', [{'service': {'struct': 'api'}}])
    write_structure(tmp_path, 'api', [{'database': {'struct': 'db'}}])
    write_structure(tmp_path, 'db')

    graph = build_command().build_graph('app', structures_path=str(tmp_path))

    assert {'from': 'app', 'to': 'api', 'folder': 'service'} in graph['edges']
    assert {'from': 'api', 'to': 'db', 'folder': 'database'} in graph['edges']


def test_graph_missing_dependency(tmp_path):
    write_structure(tmp_path, 'app', [{'missing': {'struct': 'does-not-exist'}}])

    graph = build_command().build_graph('app', structures_path=str(tmp_path))

    assert graph['missing'][0]['from'] == 'app'
    assert graph['missing'][0]['to'] == 'does-not-exist'
    assert any(node['name'] == 'does-not-exist' and node['missing'] for node in graph['nodes'])


def test_graph_cycle_detection(tmp_path):
    write_structure(tmp_path, 'a', [{'b-folder': {'struct': 'b'}}])
    write_structure(tmp_path, 'b', [{'a-folder': {'struct': 'a'}}])

    graph = build_command().build_graph('a', structures_path=str(tmp_path))

    assert ['a', 'b', 'a'] in graph['cycles']


def test_graph_local_yaml_json_and_mermaid(tmp_path):
    root = tmp_path / 'root.yaml'
    root.write_text(yaml.safe_dump({'folders': [{'child': {'struct': 'leaf'}}]}))
    write_structure(tmp_path, 'leaf')

    command = build_command()
    graph = command.build_graph(str(root), structures_path=str(tmp_path))
    json_text = command.format_graph(graph, 'json')
    mermaid = command.format_graph(graph, 'mermaid')

    data = json.loads(json_text)
    assert data['roots'] == [str(root)]
    assert {'from': str(root), 'to': 'leaf', 'folder': 'child'} in data['edges']
    assert mermaid.startswith('graph TD')
    assert '-->' in mermaid


def test_graph_all_lists_available_structures(tmp_path):
    write_structure(tmp_path, 'one', [{'two-folder': {'struct': 'two'}}])
    write_structure(tmp_path, 'two')

    graph = build_command().build_graph(structures_path=str(tmp_path), all_structures=True)

    assert 'one' in graph['roots']
    assert 'two' in graph['roots']
    assert {'from': 'one', 'to': 'two', 'folder': 'two-folder'} in graph['edges']


def test_mcp_graph_structure_logic_and_handler(tmp_path):
    write_structure(tmp_path, 'app', [{'lib': {'struct': 'library'}}])
    write_structure(tmp_path, 'library')
    server = StructMCPServer()

    json_text = server._graph_structure_logic('app', structures_path=str(tmp_path), output='json')
    data = json.loads(json_text)
    assert {'from': 'app', 'to': 'library', 'folder': 'lib'} in data['edges']

    result = asyncio.run(server._handle_graph_structure({
        'structure_definition': 'app',
        'structures_path': str(tmp_path),
        'output': 'mermaid',
    }))
    assert result.content[0].text.startswith('graph TD')
