---
tags:
  - mcp
---

# MCP (Model Context Protocol) Integration

The structkit tool now supports MCP (Model Context Protocol) integration, providing a programmable interface to interact with structure definitions. This enables automation and integration with other tools, particularly AI-assisted development workflows.

## Official MCP Registry

The official MCP Registry name for StructKit is `app.structkit/mcp` (reverse-DNS of [structkit.app](https://structkit.app/)). The listing is defined in `server.json` at the repository root. Registry clients should launch the stdio server with:

```bash
uvx structkit mcp --server
```

Keep `server.json` `version` (and `packages[0].version`) in sync with the package version in `pyproject.toml`. The Release Drafter version-bump PR updates both files before a GitHub Release.

Domain namespaces authenticate with DNS or HTTP proof of `structkit.app`. GitHub OIDC (`mcp-publisher login github` / `github-oidc`) only covers `io.github.*` names and will not publish `app.structkit/mcp`.

### Manual publish (maintainer)

Do not publish from a pull request. Do not commit the Ed25519 private key (`key.pem` is gitignored). Ownership verification only succeeds after a PyPI release whose long description includes the hidden README marker `<!-- mcp-name: app.structkit/mcp -->`.

1. Install [`mcp-publisher`](https://github.com/modelcontextprotocol/registry/blob/main/docs/reference/cli/commands.md).
2. Generate an Ed25519 keypair and the DNS TXT proof (from [registry authentication](https://modelcontextprotocol.io/registry/authentication)):

```bash
MY_DOMAIN="structkit.app"
openssl genpkey -algorithm Ed25519 -out key.pem
PUBLIC_KEY="$(openssl pkey -in key.pem -pubout -outform DER | tail -c 32 | base64)"
echo "${MY_DOMAIN}. IN TXT \"v=MCPv1; k=ed25519; p=${PUBLIC_KEY}\""
```

3. Add that TXT record on **structkit.app** at the DNS host where the domain is registered (the website is hosted on Lovable; Lovable is not the DNS registrar). Host and value:

```text
Host/name: structkit.app (or `@`)
Type: TXT
Value: v=MCPv1; k=ed25519; p=<PUBLIC_KEY>
```

Wait until the record is visible, for example `dig TXT structkit.app +short`.

HTTP alternative (same keypair): write `v=MCPv1; k=ed25519; p=${PUBLIC_KEY}` to a file and serve it at `https://structkit.app/.well-known/mcp-registry-auth`, then login with `mcp-publisher login http --domain structkit.app --private-key ...` instead of `login dns`.

4. Extract the private key **hex** (this is what `mcp-publisher` and the GitHub secret expect, not the PEM file) and store it as the repository secret `MCP_PRIVATE_KEY`. Do not commit it.

```bash
PRIVATE_KEY="$(openssl pkey -in key.pem -noout -text | grep -A3 "priv:" | tail -n +2 | tr -d ' :\n')"
# Store "${PRIVATE_KEY}" as GitHub Actions secret MCP_PRIVATE_KEY
```

5. Cut a GitHub Release so `structkit` is uploaded to PyPI with the README marker. Confirm the marker in that version's PyPI JSON `info.description`.
6. From the repository root:

```bash
mcp-publisher login dns --domain structkit.app --private-key "${PRIVATE_KEY}"
mcp-publisher publish
```

Published GitHub Releases also run `.github/workflows/publish-mcp-registry.yml`. That workflow authenticates with `mcp-publisher login dns --domain structkit.app --private-key …` using `secrets.MCP_PRIVATE_KEY`. If the secret is unset, login and publish are skipped and the release still succeeds. It is gated to `release: published` and does not run on pull requests.

## Available MCP Tools

### 1. list_structures
Lists all available structure definitions.

```json
{
  "name": "list_structures",
  "arguments": {
    "structures_path": "/path/to/custom/structures"  // optional
  }
}
```

**Parameters:**
- `structures_path` (optional): Custom path to structure definitions

### 2. get_structure_info
Get detailed information about a specific structure.

```json
{
  "name": "get_structure_info",
  "arguments": {
    "structure_name": "project/python",
    "structures_path": "/path/to/custom/structures"  // optional
  }
}
```

**Parameters:**
- `structure_name` (required): Name of the structure to get info about
- `structures_path` (optional): Custom path to structure definitions

### 3. generate_structure
Generate a project structure using specified definition and options.

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "project/python",
    "base_path": "/tmp/myproject",
    "output": "console",  // "console" or "files"
    "dry_run": false,
    "mappings": {
      "project_name": "MyProject",
      "author": "John Doe"
    },
    "structures_path": "/path/to/custom/structures",  // optional
    "source": "company"  // optional named source
  }
}
```

**Parameters:**
- `structure_definition` (required): Name or path to the structure definition
- `base_path` (required): Base path where the structure should be generated
- `output` (optional): Output mode - "console" for stdout or "files" for actual generation (default: "files")
- `dry_run` (optional): Perform a dry run without creating actual files (default: false)
- `mappings` (optional): Variable mappings for template substitution
- `structures_path` (optional): Custom path to structure definitions
- `source` (optional): Named source configured with `manage_sources`. The structure definition can also use a `<source>/<structure>` prefix.
- `no_hooks` (optional): Skip all pre/post hooks for safety (default: **true** for MCP calls)

### 4. get_structure_vars
Inspect variables declared by a specific structure without generating files.

```json
{
  "name": "get_structure_vars",
  "arguments": {
    "structure_name": "project/python",
    "structures_path": "/path/to/custom/structures",  // optional
    "output": "json"  // "text" or "json", optional
  }
}
```

**Parameters:**
- `structure_name` (required): Name or local YAML path of the structure to inspect
- `structures_path` (optional): Custom path to structure definitions
- `output` (optional): Output format - "text" for aligned human-readable output or "json" for machine-readable output (default: "text")

### 5. validate_structure
Validate a structure configuration YAML file.

```json
{
  "name": "validate_structure",
  "arguments": {
    "yaml_file": "/path/to/structure.yaml"
  }
}
```

**Parameters:**
- `yaml_file` (required): Path to the YAML configuration file to validate

### 6. lint_structure
Lint one or more structure YAML files or structure names for quality and safety issues.

```json
{
  "name": "lint_structure",
  "arguments": {
    "targets": ["project/python", "/path/to/.structkit.yaml"],
    "structures_path": "/path/to/custom/structures",
    "lint_all": false,
    "output": "json"
  }
}
```

**Parameters:**
- `targets` (optional): YAML file paths or structure names to lint. Required unless `lint_all` is true.
- `structures_path` (optional): Custom path to structure definitions.
- `lint_all` (optional): Lint all bundled contrib structures (default: false).
- `output` (optional): Output format - "text" or "json" (default: "text").


### 7. graph_structure
Visualize structure dependencies from `folders[].struct` references as text, JSON, or Mermaid. The tool reports nested dependencies, missing references, and cycles.

```json
{
  "name": "graph_structure",
  "arguments": {
    "structure_definition": "project/python",
    "structures_path": "/path/to/custom/structures",
    "graph_all": false,
    "output": "mermaid"
  }
}
```

**Parameters:**
- `structure_definition` (optional): Structure name or local YAML file to graph. Required unless `graph_all` is true.
- `structures_path` (optional): Custom path to structure definitions.
- `graph_all` (optional): Graph all available structures (default: false).
- `output` (optional): Output format - "text", "json", or "mermaid" (default: "text").

### 8. manage_sources
Manage named structure sources. Sources can point at local directories, GitHub repositories, or git URLs. Git-backed sources are cloned into the StructKit sources cache and refreshed when resolved or validated.

```json
{
  "name": "manage_sources",
  "arguments": {
    "action": "add",
    "name": "platform",
    "path_or_url": "github://httpdss/platform-structures@v1/structures"
  }
}
```

**Parameters:**
- `action` (required): One of `list`, `add`, `remove`, `show`, or `validate`.
- `name` (required except for `list`): Source name.
- `path_or_url` (required for `add`): Local directory, GitHub shorthand (`owner/repo`), `github://owner/repo`, or git URL.
- `config_path` (optional): Override the sources config file for this request.

## Usage

### Starting the MCP Server (FastMCP stdio / http / sse)

The MCP server uses FastMCP (v2.0+) and can run over stdio, http, or sse transports.

- stdio (default):
```bash
structkit mcp --server --transport stdio
```

- HTTP (StreamableHTTP):
```bash
structkit mcp --server --transport http --host 127.0.0.1 --port 9000 --path /mcp
```

- SSE:
```bash
structkit mcp --server --transport sse --host 0.0.0.0 --port 8080 --path /events
```

### Command Line Integration

The existing `list` and `info` commands now support an optional `--mcp` flag:

```bash
# List structures with MCP support
structkit list --mcp

# Get structure info with MCP support
structkit info project/python --mcp
```

## MCP Client Integration

### Claude Desktop Integration

Add the following to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**Linux**: `~/.config/claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "structkit": {
      "command": "structkit",
      "args": ["mcp", "--server"],
      "cwd": "/path/to/your/project"
    }
  }
}
```

### Cline/Continue Integration

For Cline (VS Code extension), add to your `.cline_mcp_settings.json`:

```json
{
  "mcpServers": {
    "structkit": {
      "command": "structkit",
      "args": ["mcp", "--server"]
    }
  }
}
```

### Custom MCP Client Integration

For any MCP-compatible client, connect over stdio with your preferred SDK:

```javascript
// Node.js example (MCP JS SDK)
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';

const transport = new StdioClientTransport({
  command: 'struct',
  args: ['mcp', '--server']
});

const client = new Client(
  {
    name: "struct-client",
    version: "1.0.0"
  },
  {
    capabilities: {}
  }
);

await client.connect(transport);
```

```python
# Python example (MCP Python SDK)
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="structkit",
        args=["mcp", "--server"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            print([t.name for t in tools.tools])

            result = await session.call_tool("list_structures", {})
            # FastMCP tools return plain text content
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```

## AI-Assisted Development Workflows

The MCP integration is particularly powerful for AI-assisted development workflows:

### Hook Safety in MCP

**Important**: For security, MCP calls to `generate_structure` skip hooks by default (`no_hooks: true`). This prevents arbitrary shell command execution when structures are generated via automation or AI tools.

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "project/python",
    "base_path": "/tmp/myproject",
    "no_hooks": true  // Default for MCP - hooks are skipped
  }
}
```

To enable hooks in MCP calls (not recommended unless you trust the structure source):

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "project/python",
    "base_path": "/tmp/myproject",
    "no_hooks": false  // Explicitly enable hooks (use with caution)
  }
}
```

See the [Hooks documentation](hooks.md) for more information about hook safety controls.

### Console Output Mode
Using `output: "console"` with `generate_structure` allows piping structure content to stdout for subsequent AI prompts:

```bash
# Generate structure content to console for AI review
structkit mcp --server | ai-tool "Review this project structure"
```

### Chaining Operations
The MCP tools can be chained together for complex workflows:

1. List available structures
2. Get detailed info about a specific structure
3. Generate the structure with custom mappings
4. Validate any custom configurations
5. Lint structures for stricter quality and safety checks

### Integration Examples

**Example 1: Generate and Review**
```json
// 1. Generate structure to console
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "project/python",
    "base_path": "/tmp/review",
    "output": "console"
  }
}

// 2. Use output as context for AI code review
```

**Example 2: Custom Structure Validation**
```json
// 1. Validate custom structure
{
  "name": "validate_structure",
  "arguments": {
    "yaml_file": "/path/to/custom-structure.yaml"
  }
}

// 2. If valid, generate using the custom structure
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "file:///path/to/custom-structure.yaml",
    "base_path": "/tmp/project"
  }
}
```

## End-to-end AI assistant workflow

Use this flow when you want an AI assistant to scaffold from an approved
StructKit template instead of inventing a repository layout from scratch. The
assistant should inspect available templates, choose one with you, preview the
generated files, and only then write to disk.

### 1. Start the MCP server

For local MCP clients that launch tools over stdio, use:

```bash
structkit mcp --server --transport stdio
```

For a long-running local HTTP endpoint during development, use:

```bash
structkit mcp --server --transport http --host 127.0.0.1 --port 9000 --path /mcp
```

### 2. Give the assistant a scoped prompt

```text
Use StructKit templates as the source of truth. List available structures,
inspect the Terraform module template, preview the generated output for a module
named "network-observability", and only write files after I approve the preview.
```

This prompt keeps the model on the approved-template path: discover, inspect,
preview, then generate.

### 3. List templates and inspect the chosen one

First, the assistant can discover the bundled templates:

```json
{
  "name": "list_structures",
  "arguments": {}
}
```

Then it can inspect the Terraform module scaffold:

```json
{
  "name": "get_structure_info",
  "arguments": {
    "structure_name": "terraform/modules/generic"
  }
}
```

For required variables, ask for the variable schema before generating:

```json
{
  "name": "get_structure_vars",
  "arguments": {
    "structure_name": "terraform/modules/generic",
    "output": "json"
  }
}
```

The bundled `terraform/modules/generic` structure declares `module_name`, so the
assistant should provide that value instead of guessing during generation.

### 4. Preview generated output

Use `output: "console"` to render the structure into the chat or tool result
without writing files:

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "terraform/modules/generic",
    "base_path": "/tmp/structkit-preview/network-observability",
    "output": "console",
    "dry_run": true,
    "mappings": {
      "module_name": "network-observability"
    },
    "no_hooks": true
  }
}
```

Review the preview for the expected source-of-truth files:

- `main.tf`
- `variables.tf`
- `outputs.tf`
- `versions.tf`
- `README.md`

If the preview is not right, adjust the selected structure or mappings rather
than asking the assistant to hand-edit a bespoke layout.

### 5. Generate approved files

After approval, call the same structure with `output: "files"` and
`dry_run: false`:

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "terraform/modules/generic",
    "base_path": "./modules/network-observability",
    "output": "files",
    "dry_run": false,
    "mappings": {
      "module_name": "network-observability"
    },
    "no_hooks": true
  }
}
```

The generated project structure now comes from the checked-in StructKit template.
Future changes to the scaffold should happen in the YAML definition, not as
one-off AI-generated folder edits.

### 6. Validate custom templates

If your team stores its own templates, point the MCP tools at that directory:

```json
{
  "name": "validate_structure",
  "arguments": {
    "yaml_file": "/path/to/company-structures/terraform/modules/service.yaml"
  }
}
```

Then generate from the same source of truth:

```json
{
  "name": "generate_structure",
  "arguments": {
    "structure_definition": "terraform/modules/service",
    "structures_path": "/path/to/company-structures",
    "base_path": "./modules/service-a",
    "output": "files",
    "mappings": {
      "module_name": "service-a"
    }
  }
}
```

## Configuration

### Environment Variables
The MCP server respects the same environment variables as the regular structkit tool:
- `STRUCTKIT_STRUCTURES_PATH`: Default path for structure definitions
- Any mapping variables used in templates

### Client Configuration Examples

#### 1. Basic Configuration
```json
{
  "command": "structkit",
  "args": ["mcp", "--server"]
}
```

#### 2. With Custom Structures Path

```json
{
  "command": "structkit",
  "args": ["mcp", "--server"],
  "env": {
    "STRUCTKIT_STRUCTURES_PATH": "/path/to/custom/structures"
  }
}
```

#### 3. With Python Virtual Environment

```json
{
  "command": "/path/to/venv/bin/python",
  "args": ["-m", "structkit.main", "mcp", "--server"],
  "cwd": "/path/to/structkit/project"
}
```

#### 4. Using Shell Script Wrapper

Create a shell script `struct-mcp.sh`:

```bash
#!/bin/bash
cd /path/to/your/project
source .venv/bin/activate
structkit mcp --server
```

Then configure your MCP client:

```json
{
  "command": "/path/to/struct-mcp.sh",
  "args": []
}
```

## Quick Start Guide

### Step 1: Install structkit with MCP support

```bash
pip install fastmcp>=2.0
# (your MCP client may also require installing the MCP SDK, e.g., `pip install mcp`)
```

### Step 2: Test MCP server

```bash
# Test that MCP server starts correctly
structkit mcp --server
# Should show: Starting MCP server...
# Press Ctrl+C to stop
```

### Step 3: Configure your MCP client

Add the configuration to your MCP client (see examples above).

### Step 4: Start using MCP tools

Once connected, you can use these tools:

- `list_structures` - Get all available structures
- `get_structure_info` - Get details about a specific structure
- `generate_structure` - Generate project structures
- `get_structure_vars` - Inspect declared structure variables
- `validate_structure` - Validate YAML configuration files
- `lint_structure` - Lint YAML files or structure names for quality and safety issues

## Troubleshooting

### Common Issues

1. **"Command not found: struct"**
   - Solution: Ensure structkit is installed and in your PATH
   - Alternative: Use full path to Python executable

2. **MCP server won't start**
   - Check if `mcp` package is installed: `pip show mcp`
   - Try running with verbose logging: `structkit mcp --server --log DEBUG`

3. **Client can't connect**
   - Verify the command and args in your client configuration
   - Test MCP server manually first
   - Check working directory and environment variables

4. **Structures not found**
   - Set `STRUCTKIT_STRUCTURES_PATH` environment variable
   - Use absolute paths in configuration
   - Verify structure files exist and are readable

### Debug Mode

```bash
# Run with debug logging
STRUCTKIT_LOG_LEVEL=DEBUG structkit mcp --server
```

## Benefits

1. **Automation**: Programmatic access to all structkit tool functionality
2. **Integration**: Easy integration with other development tools
3. **AI Workflows**: Enhanced support for AI-assisted development processes
4. **Consistency**: Same underlying logic as CLI commands
5. **Flexibility**: Support for custom paths, mappings, and output modes

## Backward Compatibility

All existing structkit tool functionality remains unchanged. The MCP integration is additive and does not affect existing workflows or commands.
