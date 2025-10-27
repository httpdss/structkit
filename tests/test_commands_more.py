import argparse
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from structkit.commands.generate import GenerateCommand
from structkit.commands.info import InfoCommand
from structkit.commands.list import ListCommand
from structkit.commands.mcp import MCPCommand
from structkit.commands.validate import ValidateCommand


@pytest.fixture
def parser():
    return argparse.ArgumentParser()


def test_generate_creates_base_path_and_console_output(parser, tmp_path):
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path / 'base')])

    # Minimal config: one file item with string content to avoid fetch
    config = {'files': [{'hello.txt': 'Hello'}], 'folders': []}

    # Ensure the input store file exists to avoid FileNotFoundError inside TemplateRenderer
    store_dir = tmp_path / 'store'
    store_dir.mkdir(parents=True, exist_ok=True)
    with open(store_dir / 'input.json', 'w') as fh:
        fh.write('{}')

    with patch.object(command, '_load_yaml_config', return_value=config), \
         patch('os.path.exists', side_effect=lambda p: False if str(tmp_path / 'base') in p else True), \
         patch('os.makedirs') as mock_makedirs, \
         patch('builtins.print') as mock_print:
        # Choose console output to avoid writing files
        args.output = 'file'  # still triggers base path creation logic
        args.input_store = str(store_dir / 'input.json')
        args.dry_run = True
        args.vars = None
        args.backup = None
        args.file_strategy = 'overwrite'
        args.global_system_prompt = None
        args.structures_path = None
        args.non_interactive = True

        command.execute(args)

        mock_makedirs.assert_called()  # base path created
        mock_makedirs.assert_called()  # base path created


def test_generate_dry_run_diff_shows_unified_diff(parser, tmp_path):
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path / 'base')])

    # Minimal config to trigger one file update
    config = {'files': [{'hello.txt': 'Hello world'}], 'folders': []}

    # Existing file with different content
    base_dir = tmp_path / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / 'hello.txt').write_text('Hello old\n')

    store_dir = tmp_path / 'store'
    store_dir.mkdir(parents=True, exist_ok=True)
    with open(store_dir / 'input.json', 'w') as fh:
        fh.write('{}')

    with patch.object(command, '_load_yaml_config', return_value=config), \
         patch('builtins.print') as mock_print:
        args.output = 'file'
        args.input_store = str(store_dir / 'input.json')
        args.dry_run = True
        args.diff = True
        args.vars = None
        args.backup = None
        args.file_strategy = 'overwrite'
        args.global_system_prompt = None
        args.structures_path = None
        args.non_interactive = True

        command.execute(args)

        # Should have printed a DRY RUN action and diff
        printed = ''.join(call.args[0] for call in mock_print.call_args_list)
        assert '[DRY RUN] update' in printed
        assert '--- a' in printed and '+++ b' in printed


def test_generate_pre_hook_failure_aborts(parser, tmp_path):
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path)])

    config = {'pre_hooks': ['exit 1'], 'files': []}

    def fake_run(cmd, shell, check, capture_output, text):
        raise subprocess.CalledProcessError(1, cmd, output='', stderr='boom')

    with patch.object(command, '_load_yaml_config', return_value=config), \
         patch('subprocess.run', side_effect=fake_run), \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        mock_create_structure.assert_not_called()


def test_generate_mappings_file_not_found(parser, tmp_path):
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path)])
    args.mappings_file = ['missing.yaml']

    with patch('os.path.exists', return_value=False):
        # Should return early without error
        command.execute(args)


def test_info_nonexistent_file_logs_error(parser):
    command = InfoCommand(parser)
    args = parser.parse_args(['does-not-exist'])

    with patch('os.path.exists', return_value=False):
        # Should just log error and return without exception
        command.execute(args)


def test_list_with_custom_structures_path(parser, tmp_path):
    command = ListCommand(parser)
    args = parser.parse_args(['-s', str(tmp_path / 'custom')])

    custom = str(tmp_path / 'custom')
    contribs = '/path/to/contribs'

    def mock_join(*parts):
        # emulate join used in list._list_structures
        if parts[-1] == '..':
            return '/path/to'  # dir of commands
        if parts[-1] == 'contribs':
            return contribs
        return '/'.join(parts)

    walk_map = {
        custom: [(custom, [], ['a.yaml'])],
        contribs: [(contribs, [], ['b.yaml'])],
    }

    def mock_walk(path):
        return walk_map.get(path, [])

    with patch('os.path.dirname', return_value='/path/to/commands'), \
         patch('os.path.realpath', return_value='/path/to/commands'), \
         patch('os.path.join', side_effect=mock_join), \
         patch('os.walk', side_effect=mock_walk), \
         patch('builtins.print') as mock_print:
        command._list_structures(args)
        mock_print.assert_called()  # printed list


def test_mcp_command_server_flag(parser):
    command = MCPCommand(parser)
    args = parser.parse_args(['--server'])

    async def fake_start(args):
        return None

    with patch.object(command, '_start_mcp_server', side_effect=fake_start) as mock_start:
        command.execute(args)
        mock_start.assert_called_once()


# ValidateCommand error-path tests on helpers

def test_validate_structure_config_errors(parser):
    v = ValidateCommand(parser)
    with pytest.raises(ValueError):
        v._validate_structure_config('not-a-list')
    with pytest.raises(ValueError):
        v._validate_structure_config(["not-a-dict"])  # non-dict item
    with pytest.raises(ValueError):
        v._validate_structure_config([{123: 'abc'}])  # non-str name
    with pytest.raises(ValueError):
        v._validate_structure_config([{ 'x': 123 }])  # non-str/non-dict content
    with pytest.raises(ValueError):
        v._validate_structure_config([{ 'x': {} }])   # dict missing keys


def test_validate_folders_config_errors(parser):
    v = ValidateCommand(parser)
    with pytest.raises(ValueError):
        v._validate_folders_config('not-a-list')
    with pytest.raises(ValueError):
        v._validate_folders_config(["not-a-dict"])  # non-dict item
    with pytest.raises(ValueError):
        v._validate_folders_config([{123: {}}])  # non-str name
    with pytest.raises(ValueError):
        v._validate_folders_config([{ 'name': 'not-a-dict' }])
    with pytest.raises(ValueError):
        v._validate_folders_config([{ 'name': {} }])  # missing 'struct'
    with pytest.raises(ValueError):
        v._validate_folders_config([{ 'name': { 'struct': 10 } }])  # invalid type
    with pytest.raises(ValueError):
        v._validate_folders_config([{ 'name': { 'struct': 'x', 'with': 'not-dict' } }])


def test_validate_variables_config_errors(parser):
    v = ValidateCommand(parser)
    with pytest.raises(ValueError):
        v._validate_variables_config('not-a-list')
    with pytest.raises(ValueError):
        v._validate_variables_config(["not-a-dict"])  # non-dict item
    with pytest.raises(ValueError):
        v._validate_variables_config([{123: {}}])  # non-str name
    with pytest.raises(ValueError):
        v._validate_variables_config([{ 'name': 'not-a-dict' }])
    with pytest.raises(ValueError):
        v._validate_variables_config([{ 'name': {} }])  # missing type
    with pytest.raises(ValueError):
        v._validate_variables_config([{ 'name': { 'type': 'bad' } }])
    with pytest.raises(ValueError):
        v._validate_variables_config([{ 'name': { 'type': 'boolean', 'default': 'yes' } }])
