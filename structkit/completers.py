import os


class ChoicesCompleter(object):
    def __init__(self, choices):
        self.choices = choices

    def __call__(self, **kwargs):
        return self.choices


class StructuresCompleter(object):
    """Dynamic completer for available structure names."""

    def __init__(self, structures_path=None):
        self.structures_path = structures_path

    def __call__(self, prefix, parsed_args, **kwargs):
        """Return list of available structure names for completion."""
        return self._get_available_structures(parsed_args)

    def _get_available_structures(self, parsed_args):
        """Get list of available structure names, similar to ListCommand logic."""
        # Get the directory where the commands are located
        this_file = os.path.dirname(os.path.realpath(__file__))
        contribs_path = os.path.join(this_file, "contribs")

        # Check if custom structures path is provided via parsed_args
        structures_path = getattr(parsed_args, 'structures_path', None) or self.structures_path

        if structures_path:
            paths_to_list = [structures_path, contribs_path]
        else:
            paths_to_list = [contribs_path]

        all_structures = set()
        for path in paths_to_list:
            if not os.path.exists(path):
                continue

            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".yaml"):
                        file_path = os.path.join(root, file)
                        rel_path = os.path.relpath(file_path, path)
                        # Remove .yaml extension
                        structure_name = rel_path[:-5]
                        all_structures.add(structure_name)

        return sorted(list(all_structures))


log_level_completer = ChoicesCompleter(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
file_strategy_completer = ChoicesCompleter(['overwrite', 'skip', 'append', 'rename', 'backup'])
structures_completer = StructuresCompleter()
