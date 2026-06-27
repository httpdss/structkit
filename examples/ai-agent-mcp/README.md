# AI agent / MCP scaffold example

Generate a project scaffold designed to give AI coding assistants clear repository instructions, task boundaries, and a StructKit template source of truth.

## Use case

Use this when creating a repo that will be edited by AI coding assistants and you want predictable project layout, documented conventions, and agent-friendly instructions.

## Command

```bash
structkit generate --vars "project_name=AI Assisted Project,description=A project scaffolded for AI-assisted development with StructKit." examples/ai-agent-mcp/.struct.yaml ./demo-ai-agent-project
```

## Expected output

- `README.md`
- `AGENTS.md`
- `.struct.yaml`
- `docs/architecture.md`
- `docs/decisions/0001-record-architecture-decisions.md`
- `tasks/backlog.md`

## Customization notes

- Commit the generated `.struct.yaml` so humans and AI agents can regenerate the agreed structure.
- Adapt `AGENTS.md` with repository-specific build, test, and review commands.
