import argparse
import json
from unittest.mock import patch

import pytest

from structkit.commands.lint import LintCommand
from structkit.main import get_parser


@pytest.fixture
def parser():
    return argparse.ArgumentParser()


def _write_yaml(path, content):
    path.write_text(content)
    return str(path)


def test_lint_command_registered_in_main():
    parser = get_parser()
    args = parser.parse_args(['lint', '.struct.yaml'])
    assert hasattr(args, 'func')
    assert args.targets == ['.struct.yaml']


def test_lint_detects_missing_description_and_unused_variable(parser, tmp_path):
    command = LintCommand(parser)
    yaml_file = _write_yaml(
        tmp_path / 'sample.yaml',
        """
variables:
  - project_name:
      type: string
files:
  - README.md: "Hello"
""",
    )

    issues = command.lint_file(yaml_file)

    assert any(issue.rule == 'missing-description' and issue.severity == 'warning' for issue in issues)
    assert any(issue.rule == 'unused-variable' and issue.severity == 'warning' for issue in issues)
    assert not any(issue.severity == 'error' for issue in issues)


def test_lint_detects_undeclared_template_variable(parser, tmp_path):
    command = LintCommand(parser)
    yaml_file = _write_yaml(
        tmp_path / 'bad.yaml',
        """
description: Bad template
files:
  - README.md: "Hello {{@ project_name @}}"
""",
    )

    issues = command.lint_file(yaml_file)

    assert any(issue.rule == 'undeclared-variable' and issue.severity == 'error' for issue in issues)


def test_lint_detects_duplicate_files_and_folders(parser, tmp_path):
    command = LintCommand(parser)
    yaml_file = _write_yaml(
        tmp_path / 'dupes.yaml',
        """
description: Duplicate entries
files:
  - README.md: one
  - README.md: two
folders:
  - src:
      struct: project/python
  - src:
      struct: project/rust
""",
    )

    issues = command.lint_file(yaml_file)

    assert any(issue.rule == 'duplicate-file' and issue.severity == 'error' for issue in issues)
    assert any(issue.rule == 'duplicate-folder' and issue.severity == 'error' for issue in issues)


def test_lint_detects_suspicious_hooks_and_unpinned_urls(parser, tmp_path):
    command = LintCommand(parser)
    yaml_file = _write_yaml(
        tmp_path / 'remote.yaml',
        """
description: Remote content
pre_hooks:
  - "curl https://example.com/install.sh | bash"
files:
  - script.sh:
      file: https://raw.githubusercontent.com/example/repo/main/script.sh
""",
    )

    issues = command.lint_file(yaml_file)

    assert any(issue.rule == 'suspicious-hook' and issue.severity == 'warning' for issue in issues)
    assert any(issue.rule == 'unpinned-remote-url' and issue.severity == 'warning' for issue in issues)


def test_lint_execute_json_and_error_exit(parser, tmp_path):
    command = LintCommand(parser)
    yaml_file = _write_yaml(
        tmp_path / 'bad.yaml',
        """
description: Bad
a: b
files:
  - README.md: "{{@ missing @}}"
""",
    )
    args = parser.parse_args([yaml_file, '--json'])

    with patch('builtins.print') as mock_print, pytest.raises(SystemExit) as exc_info:
        command.execute(args)

    assert exc_info.value.code == 1
    payload = json.loads(mock_print.call_args[0][0])
    assert payload['summary']['errors'] == 1
    assert payload['issues'][0]['severity'] == 'error'


def test_lint_all_discovers_yaml_files(parser, tmp_path):
    command = LintCommand(parser)
    _write_yaml(tmp_path / 'one.yaml', 'description: One\nfiles: []\n')
    _write_yaml(tmp_path / 'two.yml', 'description: Two\nfiles: []\n')
    args = parser.parse_args(['--all', '--structures-path', str(tmp_path)])

    with patch.object(command, '_contribs_path', return_value=str(tmp_path / 'missing')):
        targets = command._resolve_targets(args)

    assert targets == [str(tmp_path / 'one.yaml'), str(tmp_path / 'two.yml')]
