import pytest
from unittest.mock import patch, MagicMock, call
from structkit.commands.generate import GenerateCommand
import argparse

@pytest.fixture
def parser():
    return argparse.ArgumentParser()

def make_args(tmp_path, pre=None, post=None):
    # Create a minimal YAML config file
    config = {
        'files': [
            {'test.txt': {'content': 'hello'}}
        ]
    }
    if pre:
        config['pre_hooks'] = pre
    if post:
        config['post_hooks'] = post
    yaml_path = tmp_path / 'struct.yaml'
    import yaml as _yaml
    with open(yaml_path, 'w') as f:
        _yaml.safe_dump(config, f)
    return yaml_path

def test_no_hooks_runs_ok(tmp_path, parser):
    yaml_path = make_args(tmp_path)
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch.object(command, '_create_structure') as mock_create_structure, \
         patch.object(command, '_run_hooks', wraps=command._run_hooks) as mock_run_hooks:
        command.execute(args)
        # _run_hooks should be called for pre and post, but both are no-op
        assert mock_run_hooks.call_count == 2
        mock_create_structure.assert_called_once()

def test_pre_hook_runs_and_blocks_on_failure(tmp_path, parser):
    yaml_path = make_args(tmp_path, pre=['exit 1'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch('subprocess.run', side_effect=__import__('subprocess').CalledProcessError(1, 'exit 1')) as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        mock_subproc.assert_called_once()
        mock_create_structure.assert_not_called()

def test_post_hook_runs_and_blocks_on_failure(tmp_path, parser):
    yaml_path = make_args(tmp_path, post=['exit 1'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch('subprocess.run', side_effect=__import__('subprocess').CalledProcessError(1, 'exit 1')) as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Only post-hook should run, so only one call
        mock_subproc.assert_called_once()
        mock_create_structure.assert_called_once()

def test_hooks_order(tmp_path, parser):
    yaml_path = make_args(tmp_path, pre=['echo pre'], post=['echo post'])
    command = GenerateCommand(parser)
    args = parser.parse_args([f'file://{yaml_path}', str(tmp_path)])
    with patch('subprocess.run') as mock_subproc, \
         patch.object(command, '_create_structure') as mock_create_structure:
        command.execute(args)
        # Should call pre first, then post
        assert mock_subproc.call_args_list[0][0][0] == 'echo pre'
        assert mock_subproc.call_args_list[1][0][0] == 'echo post'
        mock_create_structure.assert_called_once()
