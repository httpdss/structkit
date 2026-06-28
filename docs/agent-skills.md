# Agent Skills

StructKit is designed to be used directly by AI assistants through MCP and other tool integrations. For teams that use reusable agent skills, the companion [`httpdss/structkit-skills`](https://github.com/httpdss/structkit-skills) repository provides an installable workflow skill that teaches assistants how to use StructKit safely.

## StructKit workflow skill

The [`structkit-workflows`](https://github.com/httpdss/structkit-skills) skill covers the recommended agent workflow for StructKit:

1. Discover available structures.
2. Inspect the selected structure and its variables.
3. Preview or dry-run the generation before writing files.
4. Use conservative file-conflict behavior for existing repositories.
5. Validate `.struct.yaml` files and generated output.

This is useful when you want an assistant to scaffold from approved StructKit templates instead of inventing project structure from scratch.

## Install

With Skills-compatible installers:

```bash
npx skills add httpdss/structkit-skills
```

With Hermes Agent:

```bash
hermes skills install https://raw.githubusercontent.com/httpdss/structkit-skills/main/SKILL.md --name structkit-workflows
```

## When to use it

Use the skill when an agent needs to:

- Generate a project, Terraform module, CI baseline, documentation bundle, or application scaffold with StructKit.
- Author or update reusable `.struct.yaml` structures.
- Review a StructKit generation plan before files are written.
- Package StructKit-backed workflows for repeatable use across repositories.

For lower-level tool integration, see the [MCP / AI Agent Workflow](mcp-integration.md) guide.
