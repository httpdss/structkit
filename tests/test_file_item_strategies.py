import argparse
import logging
from pathlib import Path

import pytest

from structkit.commands.generate import GenerateCommand


def _ensure_store(tmp_path):
    p = tmp_path / 'input.json'
    p.write_text('{}')
    return str(p)


def _base_args(parser, tmp_path):
    args = parser.parse_args(['struct-x', str(tmp_path / 'base')])
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
    return args


def test_backup_and_rename_strategies(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)

    base_dir = tmp_path / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)

    # existing file to trigger backup/rename
    (base_dir / 'a.txt').write_text('old')
    (base_dir / 'b.txt').write_text('old-b')

    backup_dir = tmp_path / 'backup'
    backup_dir.mkdir()

    config = {
        'files': [
            {'a.txt': {'content': 'new-a', 'config_variables': [], 'input_store': _ensure_store(tmp_path)}},
            {'b.txt': {'content': 'new-b', 'config_variables': [], 'input_store': _ensure_store(tmp_path)}},
        ],
        'folders': []
    }

    # First: backup strategy on a.txt
    args = _base_args(parser, tmp_path)
    args.backup = str(backup_dir)
    args.file_strategy = 'backup'

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(command, '_load_yaml_config', lambda *_: config)
        command.execute(args)

    logs = caplog.text
    assert 'Backed up:' in logs

    # Then: rename strategy on b.txt
    caplog.clear()
    args = _base_args(parser, tmp_path)
    args.file_strategy = 'rename'

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(command, '_load_yaml_config', lambda *_: config)
        command.execute(args)

    logs = caplog.text
    assert 'Renamed:' in logs


def test_skip_if_exists_path(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)

    base_dir = tmp_path / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)

    # existing file to trigger skip_if_exists
    (base_dir / 'skip.txt').write_text('already')

    config = {
        'files': [
            {'skip.txt': {'content': 'new', 'skip_if_exists': True, 'config_variables': [], 'input_store': _ensure_store(tmp_path)}},
        ],
        'folders': []
    }

    args = _base_args(parser, tmp_path)

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(command, '_load_yaml_config', lambda *_: config)
        command.execute(args)

    logs = caplog.text
    assert 'Skipped (exists and skip_if_exists=true)' in logs


def test_dry_run_diff_summary_counts(tmp_path, caplog):
    caplog.set_level(logging.INFO)

    parser = argparse.ArgumentParser()
    command = GenerateCommand(parser)

    base_dir = tmp_path / 'base'
    base_dir.mkdir(parents=True, exist_ok=True)

    # one existing for update, one new for create
    (base_dir / 'update.txt').write_text('old')

    config = {
        'files': [
            {'create.txt': 'x'},
            {'update.txt': 'y'},
        ],
        'folders': []
    }

    args = _base_args(parser, tmp_path)
    args.dry_run = True
    args.diff = True

    with pytest.MonkeyPatch().context() as mp:
        mp.setattr(command, '_load_yaml_config', lambda *_: config)
        command.execute(args)

    logs = caplog.text
    assert '[DRY RUN] Would' in logs or '[DRY RUN] create' in logs or '[DRY RUN] update' in logs
    assert '[DRY RUN] Would create' in logs or 'Would create' in logs or 'Would update' in logs
    # Summary counters
    assert '[DRY RUN] Would create:' in logs or 'Would create:' in logs
    assert '[DRY RUN] Would update:' in logs or 'Would update:' in logs
