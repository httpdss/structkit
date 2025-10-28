import asyncio
from structkit.commands import Command
from structkit.mcp_server import StructMCPServer


# MCP command class for starting the MCP server (FastMCP stdio only)
class MCPCommand(Command):
    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "MCP (Model Context Protocol) using FastMCP transports (stdio, http, sse)"
        parser.add_argument('--server', action='store_true', help='Start the MCP server')
        parser.add_argument('--transport', choices=['stdio', 'http', 'sse'], default='stdio', help='Transport protocol for the MCP server (default: stdio)')
        # HTTP/SSE options
        parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to bind for HTTP/SSE transports')
        parser.add_argument('--port', type=int, default=8000, help='Port to bind for HTTP/SSE transports')
        parser.add_argument('--path', type=str, default='/mcp', help='Endpoint path for HTTP/SSE transports')
        parser.add_argument('--uvicorn-log-level', dest='uvicorn_log_level', type=str, default=None, help='Log level for the HTTP server (e.g., info, warning, error)')
        parser.add_argument('--stateless-http', action='store_true', default=None, help='Use stateless HTTP mode (HTTP transport only)')
        parser.add_argument('--no-banner', dest='show_banner', action='store_false', default=True, help='Disable FastMCP startup banner')
        # Debugging options
        parser.add_argument('--debug', action='store_true', help='Enable debug mode (sets structkit and FastMCP loggers to DEBUG by default)')
        parser.add_argument(
            '--fastmcp-log-level',
            dest='fastmcp_log_level',
            type=str,
            default=None,
            help='Log level for FastMCP internals (e.g., DEBUG, INFO). Overrides --debug for FastMCP if provided')
        parser.set_defaults(func=self.execute)

    def execute(self, args):
        if args.server:
            self.logger.info(
                f"Starting FastMCP server for structkit tool (transport={args.transport})"
            )
            asyncio.run(self._start_mcp_server(args))
        else:
            print("MCP (Model Context Protocol) support for structkit tool (FastMCP)")
            print("\nAvailable options:")
            print("  --server                 Start the MCP server")
            print("  --transport {stdio|http|sse}  Transport protocol (default: stdio)")
            print("  --host HOST              Host for HTTP/SSE (default: 127.0.0.1)")
            print("  --port PORT              Port for HTTP/SSE (default: 8000)")
            print("  --path /PATH             Endpoint path for HTTP/SSE (default: /mcp)")
            print("  --stateless-http         Enable stateless HTTP mode (HTTP only)")
            print("  --no-banner              Disable FastMCP banner")
            print("  --debug                  Enable debug mode (structkit + FastMCP DEBUG; uvicorn=debug)")
            print("  --fastmcp-log-level LVL  Set FastMCP logger level (overrides --debug for FastMCP)")
            print("\nMCP tools available:")
            print("  - list_structures: List all available structure definitions")
            print("  - get_structure_info: Get detailed information about a structure")
            print("  - generate_structure: Generate structures with various options")
            print("  - validate_structure: Validate structure configuration files")
            print("\nExamples:")
            print("  structkit mcp --server --transport stdio --debug")
            print("  structkit mcp --server --transport http --host 127.0.0.1 --port 9000 --path /mcp --uvicorn-log-level debug")
            print("  structkit mcp --server --transport sse --host 0.0.0.0 --port 8080 --path /events --fastmcp-log-level DEBUG")

    async def _start_mcp_server(self, args=None):
        """Start the MCP server using the selected transport."""
        try:
            server = StructMCPServer()
            transport = getattr(args, 'transport', 'stdio') if args else 'stdio'
            # Map CLI args to server.run kwargs
            run_kwargs = {
                "transport": transport,
                "show_banner": getattr(args, 'show_banner', True) if args else True,
            }
            # Determine FastMCP logger level
            fastmcp_log_level = None
            if args:
                fastmcp_log_level = getattr(args, 'fastmcp_log_level', None)
                if not fastmcp_log_level and getattr(args, 'debug', False):
                    fastmcp_log_level = 'DEBUG'
            if fastmcp_log_level:
                run_kwargs["fastmcp_log_level"] = fastmcp_log_level

            if transport in {"http", "sse"}:
                # uvicorn expects lowercase levels like "info"/"debug"
                uvicorn_level = None
                if args:
                    uvicorn_level = getattr(args, 'uvicorn_log_level', None)
                    if not uvicorn_level and getattr(args, 'debug', False):
                        uvicorn_level = 'debug'
                    if not uvicorn_level:
                        # Default to args.log if provided, else None
                        uvicorn_level = getattr(args, 'log', None)
                run_kwargs.update({
                    "host": getattr(args, 'host', None),
                    "port": getattr(args, 'port', None),
                    "path": getattr(args, 'path', None),
                    "log_level": (uvicorn_level.lower() if isinstance(uvicorn_level, str) else uvicorn_level),
                })
                if transport == "http":
                    run_kwargs["stateless_http"] = getattr(args, 'stateless_http', None)
            await server.run(**run_kwargs)
        except Exception as e:
            self.logger.error(f"Error starting MCP server: {e}")
            raise
