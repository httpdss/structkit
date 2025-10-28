from structkit.commands import Command


# Import command class
# This class is responsible for importing a structure definition given a file path. It will create the structure in the base path provided.
class ImportCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.add_argument('import_from', type=str, help='Directory to import the structure from')
    parser.add_argument('-o', '--output-path', type=str, help='Path to the output directory', default='.')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info(f"Importing structure from {args.import_from} to {args.output_path}")

    self._import_structure(args)

  def _import_structure(self, args):
    raise NotImplementedError("This method needs to be implemented")
    # # Check if the import_from directory exists
    # if not os.path.exists(args.import_from):
    #   self.logger.error(f"Directory not found: {args.import_from}")
    #   return

    # # Define the path for the structure.yaml file
    # structure_definition = os.path.join(args.output_path, 'structure.yaml')

    # # Check if the output_path exists, if not, create it
    # if not os.path.exists(args.output_path):
    #   self.logger.warning(f"Output path not found: {args.output_path}, creating it")
    #   os.makedirs(args.output_path)

    # # Check if the structure.yaml file already exists
    # if os.path.exists(structure_definition):
    #   self.logger.warning(f"Structure definition already exists at {structure_definition}")
    #   # Ask the user if they want to overwrite the existing structure.yaml file
    #   if input("Do you want to overwrite it? (y/N) ").lower() != 'y':
    #     return

    # # Initialize the structure dictionary
    # generated_structure = {
    #   'structure': [],
    #   'folders': [],
    #   'variables': []
    # }

    # for root, dirs, files in os.walk(args.import_from):
    #   for file in files:
    #     self.logger.info(f"Processing file {file}")
    #     file_path = os.path.join(root, file)
    #     relative_path = os.path.relpath(file_path, args.import_from)
    #     generated_structure['structure'].append(
    #       {
    #         'path': relative_path,
    #         'content': open(file_path, 'r').read()
    #       }
    #     )

    # with open(structure_definition, 'w') as f:
    #   self.logger.info(f"Writing structure definition to {structure_definition}")
    #   yaml.dump(generated_structure, f)
