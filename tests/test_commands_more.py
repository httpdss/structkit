import argparse
import subprocess
from unittest.mock import patch, MagicMock

import pytest

from structkit.commands.generate import GenerateCommand
from structkit.commands.info import InfoCommand
from structkit.commands.list import ListCommand
from structkit.commands.mcp import MCPCommand
from structkit.commands.validate import ValidateCommand
from structkit.file_item import ContentFetchError
from structkit.input_store import InputStoreError
from structkit.template_renderer import TemplateVariableError


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


def test_generate_reports_template_variable_error_without_traceback(parser, tmp_path, caplog):
    command = GenerateCommand(parser)
    args = parser.parse_args(['struct-x', str(tmp_path)])
    args.structures_path = None
    args.mappings_file = None
    args.backup = None

    with patch.object(command, '_load_yaml_config', return_value={'files': [], 'folders': []}), \
         patch.object(command, '_create_structure', side_effect=TemplateVariableError(
             "Variable 'environment' must be one of: dev, staging, prod. Got: qa."
         )):
        with pytest.raises(SystemExit) as excinfo:
            command.execute(args)

    assert excinfo.value.code == 1
    assert "Variable 'environment' must be one of: dev, staging, prod. Got: qa." in caplog.text
    assert "Traceback" not in caplog.text


def test_generate_invalid_yaml_reports_clean_error_without_side_effect(parser, tmp_path, caplog):
    command = GenerateCommand(parser)
    invalid = tmp_path / 'invalid.yaml'
    invalid.write_text('files: [\n')
    out_dir = tmp_path / 'out-invalid'
    args = parser.parse_args(['--non-interactive', str(invalid), str(out_dir)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert f"Invalid YAML in {invalid}" in caplog.text
    assert "Traceback" not in caplog.text
    assert not out_dir.exists()


def test_generate_top_level_non_mapping_reports_clean_error_without_side_effect(parser, tmp_path, caplog):
    command = GenerateCommand(parser)
    non_mapping = tmp_path / 'list.yaml'
    non_mapping.write_text('- item\n')
    out_dir = tmp_path / 'out-list'
    args = parser.parse_args(['--non-interactive', str(non_mapping), str(out_dir)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert "Top-level YAML content must be a mapping." in caplog.text
    assert "Traceback" not in caplog.text
    assert not out_dir.exists()


def test_generate_missing_file_reports_clean_error_without_side_effect(parser, tmp_path, caplog):
    command = GenerateCommand(parser)
    missing = tmp_path / 'missing.yaml'
    out_dir = tmp_path / 'out-missing'
    args = parser.parse_args(['--non-interactive', str(missing), str(out_dir)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert f"File not found: {missing}" in caplog.text
    assert "Traceback" not in caplog.text
    assert not out_dir.exists()


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


def test_validate_missing_file_reports_clean_error(parser, tmp_path, caplog):
    command = ValidateCommand(parser)
    missing = tmp_path / 'missing.yaml'
    args = parser.parse_args([str(missing)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert f"File not found: {missing}" in caplog.text
    assert "Traceback" not in caplog.text


def test_validate_invalid_yaml_reports_clean_error(parser, tmp_path, caplog):
    command = ValidateCommand(parser)
    invalid = tmp_path / 'invalid.yaml'
    invalid.write_text('files: [\n')
    args = parser.parse_args([str(invalid)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert f"Invalid YAML in {invalid}" in caplog.text
    assert "while parsing" in caplog.text
    assert "Traceback" not in caplog.text


def test_validate_invalid_config_reports_clean_error(parser, tmp_path, caplog):
    command = ValidateCommand(parser)
    invalid_config = tmp_path / 'invalid-config.yaml'
    invalid_config.write_text('files:\n  - out.txt: {}\n')
    args = parser.parse_args([str(invalid_config)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert "Invalid structure config" in caplog.text
    assert "Dictionary item 'out.txt' must contain" in caplog.text
    assert "Traceback" not in caplog.text


def test_validate_top_level_non_mapping_reports_clean_error(parser, tmp_path, caplog):
    command = ValidateCommand(parser)
    invalid_config = tmp_path / 'list.yaml'
    invalid_config.write_text('- item\n')
    args = parser.parse_args([str(invalid_config)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert "Top-level YAML content must be a mapping." in caplog.text
    assert "Traceback" not in caplog.text


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


def test_generate_missing_local_file_ref_exits_cleanly(parser, tmp_path, caplog):
    """Missing file:// target exits 1 with root-cause message and no Traceback."""
    command = GenerateCommand(parser)
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    struct_yaml = tmp_path / 'struct.yaml'
    struct_yaml.write_text(
        'files:\n'
        '  - out.txt:\n'
        '      file: file:///tmp/does-not-exist-structkit-test.txt\n'
    )

    args = parser.parse_args(['--non-interactive', str(struct_yaml), str(out_dir)])

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert 'Failed to fetch content from' in caplog.text
    assert 'does-not-exist-structkit-test.txt' in caplog.text
    assert 'Traceback' not in caplog.text
    # The output file must NOT have been created
    assert not (out_dir / 'out.txt').exists()


def test_generate_remote_fetch_failure_exits_cleanly(parser, tmp_path, caplog):
    """Mocked remote fetch failure exits 1 with root-cause message and no Traceback."""
    command = GenerateCommand(parser)
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    config = {
        'files': [{'out.txt': {'file': 'https://example.com/no-such-file.txt'}}],
        'folders': [],
    }

    store_dir = tmp_path / 'store'
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / 'input.json').write_text('{}')

    with patch.object(command, '_load_yaml_config', return_value=config), \
         patch(
             'structkit.content_fetcher.ContentFetcher._fetch_http_url',
             side_effect=ConnectionError('network unreachable'),
         ):
        args = argparse.Namespace(
            structure_definition='dummy',
            base_path=str(out_dir),
            structures_path=None,
            dry_run=False,
            diff=False,
            output='file',
            vars=None,
            backup=None,
            file_strategy='overwrite',
            global_system_prompt=None,
            input_store=str(store_dir / 'input.json'),
            non_interactive=True,
            mappings_file=None,
            source=None,
        )
        with pytest.raises(SystemExit) as excinfo:
            command.execute(args)

    assert excinfo.value.code == 1
    assert 'Failed to fetch content from' in caplog.text
    assert 'Traceback' not in caplog.text
    assert not (out_dir / 'out.txt').exists()


# ---------------------------------------------------------------------------
# InputStore tests
# ---------------------------------------------------------------------------

def test_input_store_relative_path_does_not_crash(tmp_path):
    """A bare filename like 'input.json' must not cause makedirs('') crash."""
    import os
    from structkit.input_store import InputStore

    orig = os.getcwd()
    try:
        os.chdir(tmp_path)
        store = InputStore('input.json')
        store.load()
        assert store.get_data() == {}
        store.set_value('key', 'value')
        store.save()
        store2 = InputStore('input.json')
        store2.load()
        assert store2.get_data() == {'key': 'value'}
    finally:
        os.chdir(orig)


def test_generate_corrupt_input_store_exits_cleanly(parser, tmp_path, caplog):
    """Corrupt JSON in the input-store exits 1 with a clean message and no Traceback."""
    command = GenerateCommand(parser)
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    # Write corrupt JSON
    store_file = tmp_path / 'input.json'
    store_file.write_text('{ not valid json')

    struct_yaml = tmp_path / 'struct.yaml'
    struct_yaml.write_text('files:\n  - hello.txt: Hello\n')

    args = parser.parse_args(['--non-interactive', str(struct_yaml), str(out_dir)])
    args.input_store = str(store_file)

    with pytest.raises(SystemExit) as excinfo:
        command.execute(args)

    assert excinfo.value.code == 1
    assert 'invalid JSON' in caplog.text
    assert 'Traceback' not in caplog.text


def test_generate_unreadable_input_store_exits_cleanly(parser, tmp_path, caplog):
    """An OSError reading the input store exits 1 with a clean message and no Traceback."""
    command = GenerateCommand(parser)
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    struct_yaml = tmp_path / 'struct.yaml'
    struct_yaml.write_text('files:\n  - hello.txt: Hello\n')

    args = parser.parse_args(['--non-interactive', str(struct_yaml), str(out_dir)])
    args.input_store = str(tmp_path / 'input.json')

    with patch('builtins.open', side_effect=PermissionError('permission denied')):
        with pytest.raises(SystemExit) as excinfo:
            command.execute(args)

    assert excinfo.value.code == 1
    assert 'Traceback' not in caplog.text


# ---------------------------------------------------------------------------
# Template variable validation normalization (issue 167)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("var_value,constraint,expected_fragment", [
    ("Invalid Slug!", {"type": "string", "pattern": "^[a-z0-9-]+$"}, "does not match"),
    (0,              {"type": "integer", "min": 1},                    ">= 1"),
    (99,             {"type": "integer", "max": 10},                   "<= 10"),
])
def test_generate_validation_error_exits_cleanly(parser, tmp_path, caplog, var_value, constraint, expected_fragment):
    """Regex/min/max violations exit 1 with a clean message and no Traceback."""
    command = GenerateCommand(parser)
    out_dir = tmp_path / 'out'
    out_dir.mkdir()

    config = {
        'variables': [{'val': constraint}],
        'files': [{'out.txt': {'content': '{{@ val @}}'}}],
        'folders': [],
    }

    store_dir = tmp_path / 'store'
    store_dir.mkdir()
    (store_dir / 'input.json').write_text('{}')

    with patch.object(command, '_load_yaml_config', return_value=config):
        args = argparse.Namespace(
            structure_definition='dummy',
            base_path=str(out_dir),
            structures_path=None,
            dry_run=False,
            diff=False,
            output='file',
            vars=f'val={var_value}',
            backup=None,
            file_strategy='overwrite',
            global_system_prompt=None,
            input_store=str(store_dir / 'input.json'),
            non_interactive=True,
            mappings_file=None,
            source=None,
        )
        with pytest.raises(SystemExit) as excinfo:
            command.execute(args)

    assert excinfo.value.code == 1
    assert expected_fragment in caplog.text
    assert 'Traceback' not in caplog.text
