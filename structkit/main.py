import argparse
import logging
import os
from dotenv import load_dotenv
from structkit.utils import read_config_file, merge_configs
from structkit.commands.generate import GenerateCommand
from structkit.commands.info import InfoCommand
from structkit.commands.validate import ValidateCommand
from structkit.commands.list import ListCommand
from structkit.commands.generate_schema import GenerateSchemaCommand
from structkit.commands.mcp import MCPCommand
from structkit.logging_config import configure_logging

# Optional dependency: shtab for static shell completion generation
try:
    import shtab  # type: ignore
except Exception:  # pragma: no cover - optional at runtime
    shtab = None

load_dotenv()


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
    GenerateCommand(subparsers.add_parser('generate', help='Generate the project structure'))
    ListCommand(subparsers.add_parser('list', help='List available structures'))
    GenerateSchemaCommand(subparsers.add_parser('generate-schema', help='Generate JSON schema for available structures'))
    MCPCommand(subparsers.add_parser('mcp', help='MCP (Model Context Protocol) support'))

    # init to create a basic .struct.yaml
    from structkit.commands.init import InitCommand
    InitCommand(subparsers.add_parser('init', help='Initialize a basic .struct.yaml in the target directory'))

    # completion manager
    from structkit.commands.completion import CompletionCommand
    CompletionCommand(subparsers.add_parser('completion', help='Manage shell completions'))

    # Add shtab completion printing flags if available
    if shtab is not None:
        # Adds --print-completion and --shell flags
        shtab.add_argument_to(parser)

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
