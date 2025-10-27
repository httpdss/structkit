import pytest
import os
import argparse
from structkit.completers import log_level_completer, file_strategy_completer, structures_completer

def test_log_level_completer():
    completer = log_level_completer()
    assert 'DEBUG' in completer
    assert 'INFO' in completer
    assert 'WARNING' in completer
    assert 'ERROR' in completer
    assert 'CRITICAL' in completer

def test_file_strategy_completer():
    completer = file_strategy_completer()
    assert 'overwrite' in completer
    assert 'skip' in completer
    assert 'append' in completer
    assert 'rename' in completer
    assert 'backup' in completer

def test_structures_completer():
    # Create a mock parsed_args
    parsed_args = argparse.Namespace(structures_path=None)

    # Test the completer
    completions = structures_completer(prefix="", parsed_args=parsed_args)

    # Should return a list
    assert isinstance(completions, list)

    # Should contain some of the known structures from contribs
    # (these are based on what we saw in the directory listing)
    expected_structures = ['ansible-playbook', 'docker-files', 'helm-chart']

    # Check if at least some expected structures are present
    for expected in expected_structures:
        assert expected in completions, f"Expected '{expected}' to be in completions: {completions}"

def test_structures_completer_with_custom_path(tmp_path):
    # Create a temporary structure file
    custom_structure_file = tmp_path / "custom-structure.yaml"
    custom_structure_file.write_text("files: []")

    # Create a parsed_args with custom structures_path
    parsed_args = argparse.Namespace(structures_path=str(tmp_path))

    # Test the completer
    completions = structures_completer(prefix="", parsed_args=parsed_args)

    # Should contain the custom structure
    assert 'custom-structure' in completions
