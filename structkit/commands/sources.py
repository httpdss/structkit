from structkit.commands import Command
from structkit.sources import (
    SourceConfigError,
    add_source,
    get_source_path,
    read_sources,
    remove_source,
    validate_source,
)


class SourcesCommand(Command):
    """Manage named custom structure sources."""

    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "Manage named custom structure sources"
        subparsers = parser.add_subparsers(dest="sources_command")

        list_parser = subparsers.add_parser("list", help="List configured sources")
        list_parser.set_defaults(func=self.execute)

        add_parser = subparsers.add_parser("add", help="Add or replace a local source")
        add_parser.add_argument("name", type=str, help="Source name")
        add_parser.add_argument("path_or_url", type=str, help="Local path to structure definitions")
        add_parser.set_defaults(func=self.execute)

        remove_parser = subparsers.add_parser("remove", help="Remove a configured source")
        remove_parser.add_argument("name", type=str, help="Source name")
        remove_parser.set_defaults(func=self.execute)

        show_parser = subparsers.add_parser("show", help="Show one configured source")
        show_parser.add_argument("name", type=str, help="Source name")
        show_parser.set_defaults(func=self.execute)

        validate_parser = subparsers.add_parser("validate", help="Validate one configured source")
        validate_parser.add_argument("name", type=str, help="Source name")
        validate_parser.set_defaults(func=self.execute)

        parser.set_defaults(func=self.execute)

    def execute(self, args):
        command = getattr(args, "sources_command", None)
        if command is None:
            self.parser.print_help()
            return

        try:
            if command == "list":
                self._list_sources()
            elif command == "add":
                self._add_source(args.name, args.path_or_url)
            elif command == "remove":
                self._remove_source(args.name)
            elif command == "show":
                self._show_source(args.name)
            elif command == "validate":
                self._validate_source(args.name)
        except SourceConfigError as e:
            self.logger.error(f"❗ {e}")

    def _list_sources(self):
        sources = read_sources()
        if not sources:
            print("No sources configured")
            return
        print("📚 Configured structure sources\n")
        for name in sorted(sources):
            print(f" - {name}: {sources[name]}")

    def _add_source(self, name, path_or_url):
        source_path = add_source(name, path_or_url)
        print(f"Added source '{name}': {source_path}")

    def _remove_source(self, name):
        source_path = remove_source(name)
        print(f"Removed source '{name}': {source_path}")

    def _show_source(self, name):
        source_path = get_source_path(name)
        print(f"{name}: {source_path}")

    def _validate_source(self, name):
        source_path = validate_source(name)
        print(f"Source '{name}' is valid: {source_path}")
