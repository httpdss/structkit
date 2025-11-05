from structkit.commands import Command
import os
import json

# Generate Schema command class
class GenerateSchemaCommand(Command):
    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "Generate JSON schema for available structures"
        parser.add_argument('-s', '--structures-path', type=str, help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)', default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None))
        parser.add_argument('-o', '--output', type=str, help='Output file path for the schema (default: stdout)')
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        self.logger.info("Generating JSON schema for available structures")
        self._generate_schema(args)

    def _generate_schema(self, args):
        # Get the path to contribs directory (built-in structures)
        this_file = os.path.dirname(os.path.realpath(__file__))
        contribs_path = os.path.join(this_file, "..", "contribs")

        # Determine paths to scan
        if args.structures_path:
            final_path = args.structures_path
            paths_to_list = [final_path, contribs_path]
        else:
            paths_to_list = [contribs_path]

        # Collect all available structures
        all_structures = set()
        for path in paths_to_list:
            if os.path.exists(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        if file.endswith(".yaml"):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, path)
                            # Remove .yaml extension
                            rel_path = rel_path[:-5]
                            all_structures.add(rel_path)

        # Create JSON schema
        schema = {
            "definitions": {
                "PluginList": {
                    "enum": sorted(list(all_structures))
                }
            }
        }

        # Convert to JSON string
        json_output = json.dumps(schema, indent=2)

        # Output to file or stdout
        if args.output:
            # Create output directory if it doesn't exist
            output_dir = os.path.dirname(args.output)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            with open(args.output, 'w') as f:
                f.write(json_output)
            self.logger.info(f"Schema written to {args.output}")
            print(f"✅ Schema successfully generated at: {args.output}")
        else:
            print(json_output)
