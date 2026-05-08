import os
import yaml
import asyncio

from structkit.commands import Command
from structkit.sources import SourceConfigError, resolve_structures_path


# Info command class for exposing information about the structure
class InfoCommand(Command):

    def __init__(self, parser):
      super().__init__(parser)
      parser.description = "Show information about the package or structure definition"
      parser.add_argument('structure_definition', type=str, help='Name of the structure definition')
      parser.add_argument(
        '-s', '--structures-path', type=str, help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
        default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
      )
      parser.add_argument('--source', type=str, help='Named source containing the structure definition')
      parser.add_argument('--mcp', action='store_true', help='Enable MCP (Model Context Protocol) integration')

      parser.set_defaults(func=self.execute)

    def execute(self, args):
      self.logger.info(f"Getting info for structure {args.structure_definition}")

      if args.mcp:
        self._get_info_mcp(args)
      else:
        self._get_info(args)

    def _get_info(self, args):
      if args.structure_definition.startswith("file://") and args.structure_definition.endswith(".yaml"):
        with open(args.structure_definition[7:], 'r') as f:
          config = yaml.safe_load(f)
      else:
        try:
          effective_structures_path, structure_definition = resolve_structures_path(args, args.structure_definition)
        except SourceConfigError as e:
          self.logger.error(f"❗ {e}")
          return
        if effective_structures_path is None:
          this_file = os.path.dirname(os.path.realpath(__file__))
          file_path = os.path.join(this_file, "..", "contribs", f"{structure_definition}.yaml")
        else:
          file_path = os.path.join(effective_structures_path, f"{structure_definition}.yaml")
        # show error if file is not found
        if not os.path.exists(file_path):
          self.logger.error(f"❗ File not found: {file_path}")
          return
        with open(file_path, 'r') as f:
          config = yaml.safe_load(f)

      print("📒 Structure definition\n")
      print(f"   📌 Name: {args.structure_definition}\n")
      print(f"   📌 Description: {config.get('description', 'No description')}\n")

      if config.get('files'):
        print("   📌 Files:")
        for item in config.get('files', []):
          for name, content in item.items():
            print(f"       - {name} ")
            # indent all lines of content
            # for line in content.get('content', content.get('file', 'Not defined')).split('\n'):
            #   print(f"       {line}")

      if config.get('folders'):
        print("   📌 Folders:")
        for folder in config.get('folders', []):
          print(f"     - {folder}")
          # print(f"     - {folder}: {folder.get('struct', 'No structure')}")

    def _get_info_mcp(self, args):
      """Get structure info using MCP integration."""
      try:
        from structkit.mcp_server import StructMCPServer

        async def run_mcp_info():
          server = StructMCPServer()
          arguments = {
            "structure_name": args.structure_definition
          }
          if args.structures_path:
            arguments["structures_path"] = args.structures_path

          result = await server._handle_get_structure_info(arguments)
          return result.content[0].text

        result_text = asyncio.run(run_mcp_info())
        print(result_text)

      except ImportError:
        self.logger.error("MCP support not available. Install with: pip install mcp")
        self._get_info(args)
      except Exception as e:
        self.logger.error(f"MCP integration error: {e}")
        self.logger.info("Falling back to standard info mode")
        self._get_info(args)
