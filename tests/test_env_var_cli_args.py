import pytest
from unittest.mock import patch, MagicMock
from structkit.commands.generate import GenerateCommand
import argparse
import os


class TestGlobalSystemPromptEnvVar:
    """Tests for STRUCTKIT_GLOBAL_SYSTEM_PROMPT environment variable."""

    def test_env_var_used_when_no_cli_arg(self):
        """Test that STRUCTKIT_GLOBAL_SYSTEM_PROMPT is used when --global-system-prompt is not provided."""
        with patch.dict(os.environ, {'STRUCTKIT_GLOBAL_SYSTEM_PROMPT': 'System prompt from env'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            with patch('os.path.exists', return_value=True), \
                 patch('builtins.open', new_callable=MagicMock), \
                 patch('yaml.safe_load', return_value={'files': []}), \
                 patch.object(command, '_create_structure') as mock_create_structure:

                args = parser.parse_args(['structure.yaml', 'base_path'])
                assert args.global_system_prompt == 'System prompt from env'

    def test_cli_arg_takes_precedence_over_env_var(self):
        """Test that CLI --global-system-prompt takes precedence over env var."""
        with patch.dict(os.environ, {'STRUCTKIT_GLOBAL_SYSTEM_PROMPT': 'System prompt from env'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            with patch('os.path.exists', return_value=True), \
                 patch('builtins.open', new_callable=MagicMock), \
                 patch('yaml.safe_load', return_value={'files': []}), \
                 patch.object(command, '_create_structure') as mock_create_structure:

                args = parser.parse_args(['--global-system-prompt', 'CLI prompt', 'structure.yaml', 'base_path'])
                assert args.global_system_prompt == 'CLI prompt'


class TestInputStoreEnvVar:
    """Tests for STRUCTKIT_INPUT_STORE environment variable."""

    def test_env_var_overrides_default(self):
        """Test that STRUCTKIT_INPUT_STORE overrides the default value."""
        with patch.dict(os.environ, {'STRUCTKIT_INPUT_STORE': '/custom/input.json'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.input_store == '/custom/input.json'

    def test_default_used_when_env_var_not_set(self):
        """Test that default value is used when env var is not set."""
        env = os.environ.copy()
        env.pop('STRUCTKIT_INPUT_STORE', None)

        with patch.dict(os.environ, env, clear=True):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.input_store == '/tmp/structkit/input.json'

    def test_cli_arg_takes_precedence(self):
        """Test that CLI -n/--input-store takes precedence over env var."""
        with patch.dict(os.environ, {'STRUCTKIT_INPUT_STORE': '/env/input.json'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['--input-store', '/cli/input.json', 'structure.yaml', 'base_path'])
            assert args.input_store == '/cli/input.json'


class TestBackupPathEnvVar:
    """Tests for STRUCTKIT_BACKUP_PATH environment variable."""

    def test_env_var_used_when_no_cli_arg(self):
        """Test that STRUCTKIT_BACKUP_PATH is used when --backup is not provided."""
        with patch.dict(os.environ, {'STRUCTKIT_BACKUP_PATH': '/env/backup'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.backup == '/env/backup'

    def test_none_when_env_var_not_set(self):
        """Test that backup is None when env var is not set."""
        env = os.environ.copy()
        env.pop('STRUCTKIT_BACKUP_PATH', None)

        with patch.dict(os.environ, env, clear=True):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.backup is None

    def test_cli_arg_takes_precedence(self):
        """Test that CLI -b/--backup takes precedence over env var."""
        with patch.dict(os.environ, {'STRUCTKIT_BACKUP_PATH': '/env/backup'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['--backup', '/cli/backup', 'structure.yaml', 'base_path'])
            assert args.backup == '/cli/backup'


class TestFileStrategyEnvVar:
    """Tests for STRUCTKIT_FILE_STRATEGY environment variable."""

    def test_env_var_overrides_default(self):
        """Test that STRUCTKIT_FILE_STRATEGY overrides the default 'overwrite' value."""
        with patch.dict(os.environ, {'STRUCTKIT_FILE_STRATEGY': 'skip'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.file_strategy == 'skip'

    def test_default_when_env_var_not_set(self):
        """Test that default 'overwrite' is used when env var is not set."""
        env = os.environ.copy()
        env.pop('STRUCTKIT_FILE_STRATEGY', None)

        with patch.dict(os.environ, env, clear=True):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.file_strategy == 'overwrite'

    def test_cli_arg_takes_precedence(self):
        """Test that CLI -f/--file-strategy takes precedence over env var."""
        with patch.dict(os.environ, {'STRUCTKIT_FILE_STRATEGY': 'skip'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['--file-strategy', 'backup', 'structure.yaml', 'base_path'])
            assert args.file_strategy == 'backup'

    def test_all_valid_strategies_from_env(self):
        """Test that all valid strategies can be set via env var."""
        strategies = ['overwrite', 'skip', 'append', 'rename', 'backup']
        for strategy in strategies:
            with patch.dict(os.environ, {'STRUCTKIT_FILE_STRATEGY': strategy}):
                parser = argparse.ArgumentParser()
                command = GenerateCommand(parser)

                args = parser.parse_args(['structure.yaml', 'base_path'])
                assert args.file_strategy == strategy


class TestNonInteractiveEnvVar:
    """Tests for STRUCTKIT_NON_INTERACTIVE environment variable."""

    @pytest.mark.parametrize("value,expected", [
        ('true', True),
        ('1', True),
        ('yes', True),
        ('True', True),
        ('TRUE', True),
        ('Yes', True),
        ('false', False),
        ('0', False),
        ('no', False),
        ('', False),
    ])
    def test_env_var_parsing(self, value, expected):
        """Test that STRUCTKIT_NON_INTERACTIVE is correctly parsed for various values."""
        with patch.dict(os.environ, {'STRUCTKIT_NON_INTERACTIVE': value}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.non_interactive == expected

    def test_false_when_env_var_not_set(self):
        """Test that non_interactive is False when env var is not set."""
        env = os.environ.copy()
        env.pop('STRUCTKIT_NON_INTERACTIVE', None)

        with patch.dict(os.environ, env, clear=True):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.non_interactive is False

    def test_cli_flag_takes_precedence(self):
        """Test that CLI --non-interactive flag takes precedence over env var."""
        with patch.dict(os.environ, {'STRUCTKIT_NON_INTERACTIVE': 'false'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['--non-interactive', 'structure.yaml', 'base_path'])
            assert args.non_interactive is True


class TestOutputModeEnvVar:
    """Tests for STRUCTKIT_OUTPUT_MODE environment variable."""

    def test_env_var_overrides_default(self):
        """Test that STRUCTKIT_OUTPUT_MODE overrides the default 'file' value."""
        with patch.dict(os.environ, {'STRUCTKIT_OUTPUT_MODE': 'console'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.output == 'console'

    def test_default_when_env_var_not_set(self):
        """Test that default 'file' is used when env var is not set."""
        env = os.environ.copy()
        env.pop('STRUCTKIT_OUTPUT_MODE', None)

        with patch.dict(os.environ, env, clear=True):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])
            assert args.output == 'file'

    def test_cli_arg_takes_precedence(self):
        """Test that CLI -o/--output takes precedence over env var."""
        with patch.dict(os.environ, {'STRUCTKIT_OUTPUT_MODE': 'console'}):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['--output', 'file', 'structure.yaml', 'base_path'])
            assert args.output == 'file'


class TestEnvVarCombinations:
    """Tests for multiple environment variables used together."""

    def test_multiple_env_vars_set_simultaneously(self):
        """Test that multiple env vars work correctly when set together."""
        env_vars = {
            'STRUCTKIT_GLOBAL_SYSTEM_PROMPT': 'Test prompt',
            'STRUCTKIT_INPUT_STORE': '/custom/input.json',
            'STRUCTKIT_BACKUP_PATH': '/custom/backup',
            'STRUCTKIT_FILE_STRATEGY': 'backup',
            'STRUCTKIT_NON_INTERACTIVE': 'true',
            'STRUCTKIT_OUTPUT_MODE': 'console',
            'STRUCTKIT_STRUCTURES_PATH': '/custom/structures',
        }

        with patch.dict(os.environ, env_vars):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args(['structure.yaml', 'base_path'])

            assert args.global_system_prompt == 'Test prompt'
            assert args.input_store == '/custom/input.json'
            assert args.backup == '/custom/backup'
            assert args.file_strategy == 'backup'
            assert args.non_interactive is True
            assert args.output == 'console'
            assert args.structures_path == '/custom/structures'

    def test_cli_args_override_all_env_vars(self):
        """Test that CLI args override all env vars when provided."""
        env_vars = {
            'STRUCTKIT_GLOBAL_SYSTEM_PROMPT': 'Env prompt',
            'STRUCTKIT_INPUT_STORE': '/env/input.json',
            'STRUCTKIT_BACKUP_PATH': '/env/backup',
            'STRUCTKIT_FILE_STRATEGY': 'skip',
            'STRUCTKIT_NON_INTERACTIVE': 'false',
            'STRUCTKIT_OUTPUT_MODE': 'console',
        }

        with patch.dict(os.environ, env_vars):
            parser = argparse.ArgumentParser()
            command = GenerateCommand(parser)

            args = parser.parse_args([
                '--global-system-prompt', 'CLI prompt',
                '--input-store', '/cli/input.json',
                '--backup', '/cli/backup',
                '--file-strategy', 'rename',
                '--non-interactive',
                '--output', 'file',
                'structure.yaml',
                'base_path'
            ])

            assert args.global_system_prompt == 'CLI prompt'
            assert args.input_store == '/cli/input.json'
            assert args.backup == '/cli/backup'
            assert args.file_strategy == 'rename'
            assert args.non_interactive is True
            assert args.output == 'file'
