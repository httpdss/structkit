import argparse
import json
import os
from unittest.mock import patch

from structkit.commands.explain import ExplainCommand
from structkit.main import get_parser


def write_yaml(path, content):
    path.write_text(content)
    return path


def test_explain_command_registered_in_cli():
    parser = get_parser()
    args = parser.parse_args(['explain', 'project/python', '--json'])
    assert callable(args.func)
    assert args.structure_definition == 'project/python'
    assert args.json_output is True


def test_explain_nested_remote_hooks_variables_json_without_side_effects(tmp_path, capsys):
    structures = tmp_path / 'structures'
    structures.mkdir()
    base_path = tmp_path / 'out'

    write_yaml(
        structures / 'child.yaml',
        """
variables:
  - module_name:
      type: string
      default: child_default
files:
  - "{{@ module_name @}}.txt":
      file: https://example.com/template.txt
post_hooks:
  - "echo child {{@ module_name @}}"
""".lstrip(),
    )
    write_yaml(
        structures / 'root.yaml',
        """
variables:
  - project_name:
      type: string
      default: demo
pre_hooks:
  - "echo preparing {{@ project_name @}}"
files:
  - README.md:
      content: "# {{@ project_name @}}"
folders:
  - modules:
      struct: child
      with:
        module_name: "{{@ project_name | slugify @}}-module"
""".lstrip(),
    )

    parser = argparse.ArgumentParser()
    command = ExplainCommand(parser)
    args = parser.parse_args([
        '--structures-path', str(structures),
        '--vars', 'project_name=My Demo',
        '--json',
        'root',
        str(base_path),
    ])

    with patch('structkit.content_fetcher.ContentFetcher.fetch_content') as fetch_content, \
         patch('subprocess.run') as subprocess_run:
        command.execute(args)

    output = json.loads(capsys.readouterr().out)
    assert not base_path.exists()
    fetch_content.assert_not_called()
    subprocess_run.assert_not_called()
    assert output['hooks']['pre'][0]['command'] == 'echo preparing My Demo'
    assert output['hooks']['post'][0]['command'] == 'echo child my-demo-module'
    assert output['variables'][0]['name'] == 'project_name'
    assert output['variables'][0]['value'] == 'My Demo'
    assert any(folder['structs'] == ['child'] for folder in output['folders'])
    assert output['remote_files'] == [{
        'path': os.path.join(str(base_path), 'modules', 'my-demo-module.txt'),
        'content_location': 'https://example.com/template.txt',
        'structure': 'child',
        'depth': 1,
    }]


def test_explain_reports_conflict_behavior_for_existing_files(tmp_path):
    structure = write_yaml(
        tmp_path / 'struct.yaml',
        """
files:
  - existing.txt:
      content: replacement
""".lstrip(),
    )
    base_path = tmp_path / 'out'
    base_path.mkdir()
    (base_path / 'existing.txt').write_text('old')

    parser = argparse.ArgumentParser()
    command = ExplainCommand(parser)
    args = parser.parse_args(['--file-strategy', 'skip', str(structure), str(base_path)])

    explanation = command.explain(args)

    assert explanation['files'][0]['exists'] is True
    assert explanation['files'][0]['conflict_behavior'] == 'skip existing file'


def test_explain_text_output_includes_nested_and_hooks(tmp_path, capsys):
    structure = write_yaml(
        tmp_path / 'struct.yaml',
        """
pre_hooks:
  - echo hello
files:
  - README.md: hello
folders:
  - app:
      struct: []
""".lstrip(),
    )
    parser = argparse.ArgumentParser()
    command = ExplainCommand(parser)
    args = parser.parse_args([str(structure), str(tmp_path / 'out')])

    command.execute(args)

    output = capsys.readouterr().out
    assert 'Structure explanation' in output
    assert 'README.md' in output
    assert 'Hooks (not executed)' in output
    assert 'echo hello' in output
