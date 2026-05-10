from structkit.commands import Command
from structkit.sources import (
    SourceError,
    add_source,
    get_sources_config_path,
    read_sources,
    remove_source,
    validate_source_path,
)


class SourcesCommand(Command):
    """Manage named custom structure sources."""

    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "Manage named custom structure sources"
        parser.add_argument('--config-path', type=str, help='Override sources config path (env: STRUCTKIT_SOURCES_CONFIG)')
        subparsers = parser.add_subparsers(dest='sources_command')

        subparsers.add_parser('list', help='List configured sources').set_defaults(sources_func=self.list_sources)

        add_parser = subparsers.add_parser('add', help='Add or update a local source')
        add_parser.add_argument('name')
        add_parser.add_argument('path_or_url')
        add_parser.set_defaults(sources_func=self.add_source)

        remove_parser = subparsers.add_parser('remove', help='Remove a configured source')
        remove_parser.add_argument('name')
        remove_parser.set_defaults(sources_func=self.remove_source)

        show_parser = subparsers.add_parser('show', help='Show a configured source')
        show_parser.add_argument('name')
        show_parser.set_defaults(sources_func=self.show_source)

        validate_parser = subparsers.add_parser('validate', help='Validate a configured source')
        validate_parser.add_argument('name')
        validate_parser.set_defaults(sources_func=self.validate_source)

        parser.set_defaults(func=self.execute)

    def execute(self, args):
        if not hasattr(args, 'sources_func'):
            self.parser.print_help()
            return
        try:
            args.sources_func(args)
        except SourceError as exc:
            self.logger.error(f"❗ {exc}")
            raise SystemExit(1) from exc

    def list_sources(self, args):
        sources = read_sources(args.config_path)
        print(f"Sources config: {args.config_path or get_sources_config_path()}")
        if not sources:
            print("No sources configured.")
            return
        for name, path in sorted(sources.items()):
            print(f"{name}\t{path}")

    def add_source(self, args):
        path = add_source(args.name, args.path_or_url, args.config_path)
        print(f"Added source '{args.name}' -> {read_sources(args.config_path)[args.name]}")
        print(f"Sources config: {path}")

    def remove_source(self, args):
        path = remove_source(args.name, args.config_path)
        print(f"Removed source '{args.name}'")
        print(f"Sources config: {path}")

    def show_source(self, args):
        sources = read_sources(args.config_path)
        if args.name not in sources:
            raise SourceError(f"source not found: {args.name}")
        print(f"{args.name}\t{sources[args.name]}")

    def validate_source(self, args):
        sources = read_sources(args.config_path)
        if args.name not in sources:
            raise SourceError(f"source not found: {args.name}")
        ok, message = validate_source_path(sources[args.name])
        if not ok:
            raise SourceError(message)
        print(f"Source '{args.name}' is valid: {message}")
