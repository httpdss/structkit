import argparse
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock

from structkit.commands.search import SearchCommand


@pytest.fixture
def parser():
    return argparse.ArgumentParser()


def _make_args(parser, query, structures_path=None, names_only=False):
    cmd = SearchCommand(parser)
    argv = [query]
    if structures_path:
        argv += ['-s', structures_path]
    if names_only:
        argv.append('--names-only')
    args = parser.parse_args(argv)
    return cmd, args


def test_search_match_by_name(parser):
    """Structures whose name matches the query are returned."""
    cmd, args = _make_args(parser, 'docker')

    yaml_content = b'files: []'
    walk_data = [('/fake/contribs', [], ['docker-files.yaml', 'helm-chart.yaml'])]

    def fake_open(path, *a, **kw):
        return mock_open(read_data=yaml_content)()

    with patch('os.path.dirname', return_value='/fake/commands'), \
         patch('os.path.realpath', return_value='/fake/commands'), \
         patch('os.path.join', side_effect=lambda *parts: '/'.join(parts)), \
         patch('os.walk', return_value=walk_data), \
         patch('os.path.relpath', side_effect=lambda fp, base: os.path.basename(fp)), \
         patch('builtins.open', side_effect=fake_open), \
         patch('yaml.safe_load', return_value={}), \
         patch('builtins.print') as mock_print:
        cmd._search_structures(args)

    printed = ' '.join(str(c) for c in mock_print.call_args_list)
    assert 'docker-files' in printed
    assert 'helm-chart' not in printed


def test_search_match_by_description(parser):
    """Structures whose description matches the query are returned."""
    cmd, args = _make_args(parser, 'kubernetes')

    configs = {
        'helm-chart.yaml': {'description': 'Deploy apps to kubernetes clusters'},
        'docker-files.yaml': {},
    }
    walk_data = [('/fake/contribs', [], ['helm-chart.yaml', 'docker-files.yaml'])]

    # Track which file is currently being opened so yaml.safe_load can return the right config
    current_path = [None]

    def fake_open(path, *a, **kw):
        current_path[0] = path
        return mock_open(read_data=b'')()

    def fake_yaml_load(f):
        for basename, config in configs.items():
            if current_path[0] and current_path[0].endswith(basename):
                return config
        return {}

    with patch('os.path.dirname', return_value='/fake/commands'), \
         patch('os.path.realpath', return_value='/fake/commands'), \
         patch('os.path.join', side_effect=lambda *parts: '/'.join(parts)), \
         patch('os.walk', return_value=walk_data), \
         patch('os.path.relpath', side_effect=lambda fp, base: os.path.basename(fp)), \
         patch('builtins.open', side_effect=fake_open), \
         patch('yaml.safe_load', side_effect=fake_yaml_load), \
         patch('builtins.print') as mock_print:
        cmd._search_structures(args)

    printed = ' '.join(str(c) for c in mock_print.call_args_list)
    assert 'helm-chart' in printed
    assert 'docker-files' not in printed


def test_search_no_results(parser):
    """No-match query prints an appropriate message."""
    cmd, args = _make_args(parser, 'xyznotfound')

    walk_data = [('/fake/contribs', [], ['docker-files.yaml'])]

    with patch('os.path.dirname', return_value='/fake/commands'), \
         patch('os.path.realpath', return_value='/fake/commands'), \
         patch('os.path.join', side_effect=lambda *parts: '/'.join(parts)), \
         patch('os.walk', return_value=walk_data), \
         patch('os.path.relpath', side_effect=lambda fp, base: os.path.basename(fp)), \
         patch('builtins.open', mock_open(read_data=b'{}')), \
         patch('yaml.safe_load', return_value={}), \
         patch('builtins.print') as mock_print:
        cmd._search_structures(args)

    printed = ' '.join(str(c) for c in mock_print.call_args_list)
    assert 'No structures found' in printed


def test_search_names_only(parser):
    """--names-only prints bare names without decoration."""
    cmd, args = _make_args(parser, 'docker', names_only=True)

    walk_data = [('/fake/contribs', [], ['docker-files.yaml', 'docker-compose.yaml'])]

    with patch('os.path.dirname', return_value='/fake/commands'), \
         patch('os.path.realpath', return_value='/fake/commands'), \
         patch('os.path.join', side_effect=lambda *parts: '/'.join(parts)), \
         patch('os.walk', return_value=walk_data), \
         patch('os.path.relpath', side_effect=lambda fp, base: os.path.basename(fp)), \
         patch('builtins.open', mock_open(read_data=b'{}')), \
         patch('yaml.safe_load', return_value={}), \
         patch('builtins.print') as mock_print:
        cmd._search_structures(args)

    calls = [str(c.args[0]) for c in mock_print.call_args_list]
    # Should only print plain names, no emoji or bullet prefix
    assert all('🔍' not in c and ' - ' not in c for c in calls)
    assert any('docker-compose' in c for c in calls)
    assert any('docker-files' in c for c in calls)


def test_search_custom_structures_path(parser, tmp_path):
    """Custom --structures-path structures appear with '+' marker."""
    custom_yaml = tmp_path / 'my-custom.yaml'
    custom_yaml.write_text('description: my custom structure\n')

    cmd = SearchCommand(parser)
    args = parser.parse_args(['custom', '-s', str(tmp_path)])

    with patch('builtins.print') as mock_print:
        cmd._search_structures(args)

    printed = ' '.join(str(c) for c in mock_print.call_args_list)
    assert 'my-custom' in printed
    assert '+' in printed


def test_search_command_registered_in_main():
    """The search subcommand is registered in the main parser."""
    from structkit.main import get_parser
    parser = get_parser()
    # If 'search' is not registered, parse_args will error
    args = parser.parse_args(['search', 'docker'])
    assert hasattr(args, 'func')
    assert args.query == 'docker'
