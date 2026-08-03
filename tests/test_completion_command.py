import argparse
import os
from unittest.mock import patch

from structkit.commands.completion import CompletionCommand
from structkit.main import get_parser


def make_parser():
    return argparse.ArgumentParser()


def _gather_print_output(mock_print):
    return "\n".join(str(call.args[0]) for call in mock_print.call_args_list)


def test_completion_install_bash_explicit():
    parser = make_parser()
    cmd = CompletionCommand(parser)
    with patch('builtins.print') as mock_print:
        args = parser.parse_args(['install', 'bash'])
        cmd._install(args)
        out = _gather_print_output(mock_print)
        assert "Detected shell: bash" in out
        assert "structkit --print-completion bash" in out
        assert "~/.local/share/bash-completion/completions/structkit" in out


def test_completion_install_zsh_explicit():
    parser = make_parser()
    cmd = CompletionCommand(parser)
    with patch('builtins.print') as mock_print:
        args = parser.parse_args(['install', 'zsh'])
        cmd._install(args)
        out = _gather_print_output(mock_print)
        assert "Detected shell: zsh" in out
        assert "structkit --print-completion zsh" in out
        assert "~/.zfunc/_structkit" in out


def test_completion_install_fish_explicit():
    parser = make_parser()
    cmd = CompletionCommand(parser)
    with patch('builtins.print') as mock_print:
        args = parser.parse_args(['install', 'fish'])
        cmd._install(args)
        out = _gather_print_output(mock_print)
        assert "Detected shell: fish" in out
        assert "structkit --print-completion fish" in out
        assert "~/.config/fish/completions/structkit.fish" in out
        assert "pip install shtab" not in out


def test_completion_install_auto_detect_zsh():
    parser = make_parser()
    cmd = CompletionCommand(parser)
    with patch.dict(os.environ, {"SHELL": "/bin/zsh"}, clear=False):
        with patch('builtins.print') as mock_print:
            args = parser.parse_args(['install'])
            cmd._install(args)
            out = _gather_print_output(mock_print)
            assert "Detected shell: zsh" in out
            assert "structkit --print-completion zsh" in out


def test_print_completion_fish_generates_a_fish_script(capsys):
    parser = get_parser()

    try:
        parser.parse_args(['--print-completion', 'fish'])
    except SystemExit as error:
        assert error.code == 0

    output = capsys.readouterr().out
    assert "function __fish_structkit_using_command" in output
    assert "complete -c structkit -f" in output
    assert "complete -c structkit -n __fish_structkit_using_command -a generate" in output
    assert " -s h -d " in output
    assert " -l print-completion -r -a 'bash zsh tcsh fish'" in output
