from structkit.commands import Command
import os
import asyncio


# List command class
class ListCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.description = "List available structures"
    parser.add_argument(
      '-s', '--structures-path', type=str, help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
      default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
    )
    parser.add_argument('--names-only', action='store_true', help='Print only structure names, one per line (for shell completion)')
    parser.add_argument('--mcp', action='store_true', help='Enable MCP (Model Context Protocol) integration')
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info("Listing available structures")
    if args.mcp:
      self._list_structures_mcp(args)
    else:
      self._list_structures(args)

  def _list_structures(self, args):
    this_file = os.path.dirname(os.path.realpath(__file__))
    contribs_path = os.path.join(this_file, "..", "contribs")

    if args.structures_path:
      final_path = args.structures_path
      paths_to_list = [final_path, contribs_path]
    else:
      paths_to_list = [contribs_path]

    all_structures = set()
    for path in paths_to_list:
      for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, path)
            if file.endswith(".yaml"):
              rel_path = rel_path[:-5]
              # Mark custom path entries with '+ ' unless names-only requested
              if not args.names_only and path != contribs_path:
                rel_path = f"+ {rel_path}"
              all_structures.add(rel_path)

    sorted_list = sorted(all_structures)

    if args.names_only:
      # Print plain names without bullets or headers, remove '+ ' marker
      for structure in sorted_list:
        if structure.startswith('+ '):
          print(structure[2:])
        else:
          print(structure)
      return

    print("📃 Listing available structures\n")
    for structure in sorted_list:
      print(f" - {structure}")

    print("\nUse 'structkit generate' to generate the structure")
    print("Note: Structures with '+' sign are custom structures")

  def _list_structures_mcp(self, args):
    """List structures using MCP integration."""
    try:
      from structkit.mcp_server import StructMCPServer

      async def run_mcp_list():
        server = StructMCPServer()
        arguments = {}
        if args.structures_path:
          arguments["structures_path"] = args.structures_path

        result = await server._handle_list_structures(arguments)
        return result.content[0].text

      result_text = asyncio.run(run_mcp_list())
      print(result_text)

    except ImportError:
      self.logger.error("MCP support not available. Install with: pip install mcp")
      self._list_structures(args)
    except Exception as e:
      self.logger.error(f"MCP integration error: {e}")
      self.logger.info("Falling back to standard list mode")
      self._list_structures(args)
