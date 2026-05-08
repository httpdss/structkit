import os
import yaml

from structkit.commands import Command
from structkit.sources import SourceConfigError, resolve_structures_path


class SearchCommand(Command):
    """Search available structures by keyword (matches name and description)."""

    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "Search available structures by keyword"
        parser.add_argument(
            'query',
            type=str,
            help='Search term to match against structure names and descriptions',
        )
        parser.add_argument(
            '-s', '--structures-path',
            type=str,
            help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
            default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None),
        )
        parser.add_argument(
            '--source',
            type=str,
            help='Named source to search',
        )
        parser.add_argument(
            '--names-only',
            action='store_true',
            help='Print only matching structure names, one per line (for scripting)',
        )
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        self.logger.info(f"Searching structures for '{args.query}'")
        self._search_structures(args)

    def _search_structures(self, args):
        this_file = os.path.dirname(os.path.realpath(__file__))
        contribs_path = os.path.join(this_file, '..', 'contribs')

        try:
            effective_structures_path, _ = resolve_structures_path(args)
        except SourceConfigError as e:
            self.logger.error(f"❗ {e}")
            return

        if effective_structures_path:
            paths_to_search = [(effective_structures_path, False), (contribs_path, True)]
        else:
            paths_to_search = [(contribs_path, True)]

        query = args.query.lower()
        matches = []

        for path, is_contribs in paths_to_search:
            for root, _, files in os.walk(path):
                for file in files:
                    if not file.endswith('.yaml'):
                        continue
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)
                    name = rel_path[:-5]  # strip .yaml

                    description = ''
                    try:
                        with open(file_path, 'r') as f:
                            config = yaml.safe_load(f) or {}
                        description = config.get('description', '') or ''
                    except Exception:
                        pass

                    if query in name.lower() or query in description.lower():
                        is_custom = not is_contribs
                        matches.append((name, description, is_custom))

        matches.sort(key=lambda x: x[0])

        if args.names_only:
            for name, _, _ in matches:
                print(name)
            return

        if not matches:
            print(f"No structures found matching '{args.query}'")
            return

        print(f"🔍 Search results for '{args.query}'\n")
        for name, description, is_custom in matches:
            prefix = '+ ' if is_custom else '  '
            desc_str = f" — {description}" if description else ''
            print(f" {prefix}{name}{desc_str}")

        print("\nUse 'structkit generate' to generate a structure")
        print("Note: Structures with '+' sign are custom structures")
