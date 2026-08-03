import argparse
import logging
import os
import shlex
from dotenv import load_dotenv
from structkit.utils import read_config_file, merge_configs
from structkit.commands.generate import GenerateCommand
from structkit.commands.info import InfoCommand
from structkit.commands.vars import VarsCommand
from structkit.commands.explain import ExplainCommand
from structkit.commands.validate import ValidateCommand
from structkit.commands.lint import LintCommand
from structkit.commands.list import ListCommand
from structkit.commands.search import SearchCommand
from structkit.commands.graph import GraphCommand
from structkit.commands.generate_schema import GenerateSchemaCommand
from structkit.commands.mcp import MCPCommand
from structkit.commands.sources import SourcesCommand
from structkit.logging_config import configure_logging

# Optional dependency: shtab for static shell completion generation
try:
    import shtab  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    shtab = None

load_dotenv()
SUPPORTED_COMPLETION_SHELLS = ("bash", "zsh", "tcsh", "fish")


def _fish_quote(value):
    return shlex.quote(str(value))


def _fish_condition(command_path):
    if not command_path:
        return "__fish_structkit_using_command"
    return "__fish_structkit_using_command " + " ".join(_fish_quote(command) for command in command_path)


def _fish_completion_script(parser):
    """Generate a static Fish completion script from an argparse parser."""
    lines = [
      "function __fish_structkit_using_command",
      "    set -l words (commandline -opc)",
      "    set -e words[1]",
      "    set -l commands",
      "    for word in $words",
      "        if not string match -qr '^-' -- $word",
      "            set -a commands $word",
      "        end",
      "    end",
      "    test (count $commands) -eq (count $argv)",
      "    or return 1",
      "    for index in (seq (count $argv))",
      "        test \"$commands[$index]\" = \"$argv[$index]\"",
      "        or return 1",
      "    end",
      "end",
      "",
      f"complete -c {_fish_quote(parser.prog)} -f",
    ]

    def add_completions(current_parser, command_path=()):
        condition = _fish_condition(command_path)
        for action in current_parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                for name, subparser in action.choices.items():
                    if name not in action._name_parser_map:
                        continue
                    help_text = action._name_parser_map[name].description or ""
                    command = (
                      f"complete -c {_fish_quote(parser.prog)} -n {_fish_quote(condition)} "
                      f"-a {_fish_quote(name)}"
                    )
                    if help_text:
                        command += f" -d {_fish_quote(help_text)}"
                    lines.append(command)
                    add_completions(subparser, command_path + (name,))
                continue

            if action.help is argparse.SUPPRESS:
                continue

            choices = getattr(action, "choices", None)
            arguments = ""
            if choices:
                arguments = " -a " + _fish_quote(" ".join(map(str, choices)))

            for option in action.option_strings:
                option_type = "-l" if option.startswith("--") else "-s"
                command = (
                  f"complete -c {_fish_quote(parser.prog)} -n {_fish_quote(condition)} "
                  f"{option_type} {_fish_quote(option.lstrip('-'))}"
                )
                if action.nargs != 0:
                    command += " -r"
                command += arguments
                if action.help:
                    command += f" -d {_fish_quote(action.help)}"
                lines.append(command)

    add_completions(parser)
    return "\n".join(lines)


class PrintCompletionAction(argparse.Action):
    """Print a completion script for shtab-supported shells or Fish."""

    def __call__(self, parser, namespace, values, option_string=None):
        if values == "fish":
            print(_fish_completion_script(parser))
        else:
            print(shtab.complete(parser, values))
        parser.exit(0)


def get_parser():
    parser = argparse.ArgumentParser(
      description="Generate project structure from YAML configuration.",
      prog="structkit",
      epilog="Thanks for using %(prog)s! :)",
    )

    # Create subparsers
    subparsers = parser.add_subparsers()

    InfoCommand(subparsers.add_parser('info', help='Show information about the package'))
    ValidateCommand(subparsers.add_parser('validate', help='Validate the YAML configuration file'))
    LintCommand(subparsers.add_parser('lint', help='Lint structure YAML files for quality issues'))
    GenerateCommand(subparsers.add_parser('generate', help='Generate the project structure'))
    VarsCommand(subparsers.add_parser('vars', help='Inspect structure variables'))
    ExplainCommand(subparsers.add_parser('explain', help='Explain structure resolution without generating files'))
    ListCommand(subparsers.add_parser('list', help='List available structures'))
    SearchCommand(subparsers.add_parser('search', help='Search available structures by keyword'))
    GraphCommand(subparsers.add_parser('graph', help='Visualize structure dependencies'))
    GenerateSchemaCommand(subparsers.add_parser('generate-schema', help='Generate JSON schema for available structures'))
    MCPCommand(subparsers.add_parser('mcp', help='MCP (Model Context Protocol) support'))
    SourcesCommand(subparsers.add_parser('sources', help='Manage named custom structure sources'))

    # init to create a basic .struct.yaml
    from structkit.commands.init import InitCommand
    InitCommand(subparsers.add_parser('init', help='Initialize a basic .struct.yaml in the target directory'))

    # completion manager
    from structkit.commands.completion import CompletionCommand
    CompletionCommand(subparsers.add_parser('completion', help='Manage shell completions'))

    # shtab supports bash, zsh, and tcsh. Fish is generated locally.
    if shtab is not None:
        parser.add_argument(
          "--print-completion",
          choices=SUPPORTED_COMPLETION_SHELLS,
          action=PrintCompletionAction,
          help="print shell completion script",
        )

    return parser


def main():
    parser = get_parser()

    args = parser.parse_args()

    # Check if a subcommand was provided
    if not hasattr(args, 'func'):
      parser.print_help()
      parser.exit()

    # Read config file if provided
    if getattr(args, 'config_file', None):
      file_config = read_config_file(args.config_file)
      args = argparse.Namespace(**merge_configs(file_config, args))

    # Resolve logging level precedence: STRUCTKIT_LOG_LEVEL env > --debug (if present) > --log
    env_level = os.getenv('STRUCTKIT_LOG_LEVEL')
    if env_level:
        logging_level = getattr(logging, env_level.upper(), logging.INFO)
    else:
        # Some commands (like mcp) may add a --debug flag; respect it
        if getattr(args, 'debug', False):
            logging_level = logging.DEBUG
        else:
            logging_level = getattr(logging, getattr(args, 'log', 'INFO').upper(), logging.INFO)

    configure_logging(level=logging_level, log_file=getattr(args, 'log_file', None))

    args.func(args)


if __name__ == "__main__":
    main()
