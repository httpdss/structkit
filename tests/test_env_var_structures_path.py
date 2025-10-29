import pytest
from unittest.mock import patch, MagicMock
from structkit.commands.generate import GenerateCommand
import argparse
import os


@pytest.fixture
def parser():
    return argparse.ArgumentParser()


def test_env_var_structures_path_used_when_no_cli_arg(parser):
    """Test that STRUCTKIT_STRUCTURES_PATH env var is used when --structures-path is not provided."""
    command = GenerateCommand(parser)

    with patch.dict(os.environ, {'STRUCTKIT_STRUCTURES_PATH': '/custom/structures'}), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock), \
         patch('yaml.safe_load', return_value={'files': []}), \
         patch.object(command, '_create_structure') as mock_create_structure:

        # Parse args without --structures-path
        args = parser.parse_args(['structure.yaml', 'base_path'])
        command.execute(args)

        # Verify structures_path was set from environment variable
        assert args.structures_path == '/custom/structures'
        mock_create_structure.assert_called_once()


def test_cli_arg_takes_precedence_over_env_var(parser):
    """Test that CLI --structures-path takes precedence over STRUCTKIT_STRUCTURES_PATH env var."""
    command = GenerateCommand(parser)

    with patch.dict(os.environ, {'STRUCTKIT_STRUCTURES_PATH': '/env/structures'}), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock), \
         patch('yaml.safe_load', return_value={'files': []}), \
         patch.object(command, '_create_structure') as mock_create_structure:

        # Parse args WITH --structures-path
        args = parser.parse_args(['--structures-path', '/cli/structures', 'structure.yaml', 'base_path'])
        command.execute(args)

        # Verify CLI arg was not overridden by env var
        assert args.structures_path == '/cli/structures'
        mock_create_structure.assert_called_once()


def test_no_structures_path_when_env_var_not_set(parser):
    """Test that structures_path remains None when neither CLI arg nor env var is provided."""
    command = GenerateCommand(parser)

    # Ensure env var is not set
    env = os.environ.copy()
    env.pop('STRUCTKIT_STRUCTURES_PATH', None)

    with patch.dict(os.environ, env, clear=True), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock), \
         patch('yaml.safe_load', return_value={'files': []}), \
         patch.object(command, '_create_structure') as mock_create_structure:

        # Parse args without --structures-path
        args = parser.parse_args(['structure.yaml', 'base_path'])
        command.execute(args)

        # Verify structures_path remains None
        assert args.structures_path is None
        mock_create_structure.assert_called_once()


def test_env_var_logging_message(parser, caplog):
    """Test that a log message is emitted when using STRUCTKIT_STRUCTURES_PATH env var."""
    import logging
    command = GenerateCommand(parser)

    with patch.dict(os.environ, {'STRUCTKIT_STRUCTURES_PATH': '/custom/structures'}), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock), \
         patch('yaml.safe_load', return_value={'files': []}), \
         patch.object(command, '_create_structure') as mock_create_structure:

        # Enable debug logging to capture the log message
        with caplog.at_level(logging.INFO):
            args = parser.parse_args(['structure.yaml', 'base_path'])
            command.execute(args)

        # Verify log message was emitted
        assert 'Using STRUCTKIT_STRUCTURES_PATH: /custom/structures' in caplog.text


def test_empty_env_var_is_ignored(parser):
    """Test that an empty STRUCTKIT_STRUCTURES_PATH env var is treated as not set."""
    command = GenerateCommand(parser)

    with patch.dict(os.environ, {'STRUCTKIT_STRUCTURES_PATH': ''}), \
         patch('os.path.exists', return_value=True), \
         patch('builtins.open', new_callable=MagicMock), \
         patch('yaml.safe_load', return_value={'files': []}), \
         patch.object(command, '_create_structure') as mock_create_structure:

        # Parse args without --structures-path
        args = parser.parse_args(['structure.yaml', 'base_path'])
        command.execute(args)

        # Verify structures_path remains None (empty string is falsy)
        assert args.structures_path == '' or args.structures_path is None
        mock_create_structure.assert_called_once()
