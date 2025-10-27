import argparse
import asyncio
import logging

import pytest

from structkit.commands.generate import GenerateCommand
from structkit.mcp_server import StructMCPServer


def _ensure_store(tmp_path):
    store_dir = tmp_path / 'store'
    store_dir.mkdir(parents=True, exist_ok=True)
    p = store_dir / 'input.json'
    p.write_text('{}')
    return str(p)


def test_generate_summary_counts_created_updated(tmp_path, caplog):
    # capture INFO logs for our modules
    caplog.set_level(logging.INFO)
    caplog.set_level(logging.INFO, logger='structkit.file_item')
    caplog.set_level(logging.INFO, logger='structkit.commands.generate')

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path / 'base')])

    base_dir = tmp_path / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)

    # Prepare one existing file (update) and one new file (create)
    (base_dir / 'update.txt').write_text('old')

    config = {
        'files': [
            {'create.txt': 'new-content'},
            {'update.txt': 'newer-content'},
        ],
        'folders': []
    }

    args.output = 'file'
    args.input_store = _ensure_store(tmp_path)
    args.dry_run = False
    args.diff = False
    args.vars = None
    args.backup = None
    args.file_strategy = 'overwrite'
    args.global_system_prompt = None
    args.structures_path = None
    args.non_interactive = True

    # Execute with mocked config
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(command, '_load_yaml_config', lambda *_: config)
        command.execute(args)

    logs = caplog.text
    assert 'Summary of actions:' in logs
    assert 'Created:' in logs and 'Updated:' in logs


def test_fileitem_append_logs_message(tmp_path, caplog):
    caplog.set_level(logging.INFO)
    caplog.set_level(logging.INFO, logger='structkit.file_item')

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path / 'base')])

    base_dir = tmp_path / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)

    # Existing file to trigger append
    (base_dir / 'append.txt').write_text('start\n')

    config = {
        'files': [
            {'append.txt': {'content': 'more', 'config_variables': [], 'input_store': _ensure_store(tmp_path)}},
        ],
        'folders': []
    }

    args.output = 'file'
    args.input_store = _ensure_store(tmp_path)
    args.dry_run = False
    args.diff = False
    args.vars = None
    args.backup = None
    args.file_strategy = 'append'
    args.global_system_prompt = None
    args.structures_path = None
    args.non_interactive = True

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(command, '_load_yaml_config', lambda *_: config)
        command.execute(args)

    logs = caplog.text
    assert 'Appended:' in logs


def test_mcp_get_structure_info_rich_rendering(tmp_path):
    # Create a temp YAML structure with folders/structkit/with
    yaml_path = tmp_path / 'my-struct.yaml'
    yaml_path.write_text(
        """
        description: Example
        files:
          - foo.txt: "bar"
        folders:
          - nested:
              struct:
                - sub/one
                - sub/two
              with:
                team: devops
                env: dev
        """
    )

    async def run():
        server = StructMCPServer()
        return await server._handle_get_structure_info({
            'structure_name': f'file://{yaml_path}',
        })

    result = asyncio.run(run())
    text = result.content[0].text
    assert 'Folders:' in text
    assert '• struct' in text or '• struct(s):' in text
    assert '• with:' in text
