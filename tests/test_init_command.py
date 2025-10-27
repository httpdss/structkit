import argparse
import os
from unittest.mock import patch

from structkit.commands.init import InitCommand, BASIC_STRUCTKIT_YAML


def test_init_creates_struct_yaml(tmp_path):
    parser = argparse.ArgumentParser()
    cmd = InitCommand(parser)

    target_dir = tmp_path / "proj"
    args = parser.parse_args([str(target_dir)])

    with patch('builtins.print') as mock_print:
        cmd.execute(args)

    struct_file = target_dir / '.struct.yaml'
    assert struct_file.exists()

    content = struct_file.read_text()
    # Basic checks for key sections
    assert 'pre_hooks:' in content
    assert 'post_hooks:' in content
    assert 'files:' in content
    assert 'README.md' in content
    assert 'folders:' in content
    assert 'github/workflows/run-struct' in content


def test_init_skips_if_exists(tmp_path):
    parser = argparse.ArgumentParser()
    cmd = InitCommand(parser)

    target_dir = tmp_path / "proj"
    target_dir.mkdir(parents=True)
    existing = target_dir / '.struct.yaml'
    existing.write_text('files: []\n')

    args = parser.parse_args([str(target_dir)])

    with patch('builtins.print') as mock_print:
        cmd.execute(args)
        # Should not overwrite existing file
        assert existing.read_text() == 'files: []\n'
        # Should print a message about skipping
        printed = "\n".join(c.args[0] for c in mock_print.call_args_list)
        assert '.struct.yaml already exists' in printed
