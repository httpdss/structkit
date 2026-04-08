---
title: Consistent Project Scaffolding at Scale with structkit
date: 2026-04-08
tags:
  - scaffolding
  - devops
  - platform-engineering
  - mcp
  - open-source
authors:
  - httpdss
---

Every engineering team eventually hits the same wall: onboarding a new service takes half a day of copying files, hunting down the right `.gitignore`, figuring out which CI template is current, and hoping the intern doesn't miss the security scanning step. The solution is usually a wiki page nobody reads, a "golden repo" that's three quarters out of date, or a Slack message to the platform team that disappears into the void.

**structkit** exists to solve this problem definitively.

<!-- more -->

## What is structkit?

structkit is an open-source project scaffolding tool that lets you define entire project structures — files, folders, content, permissions, remote assets — in a single YAML file and generate them consistently, anywhere.

Think of it as "infrastructure as code, but for your project structure."

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}
        {{@ description @}}
  - .github/workflows/ci.yml:
      file: github://your-org/templates/main/ci.yml
  - .gitignore:
      file: github://github/gitignore/main/Python.gitignore

variables:
  - project_name:
      description: "Name of your project"
  - description:
      description: "One-line project description"
```

Run `structkit generate my-template ./new-service` and you get a complete, consistent project scaffold in seconds — with the correct CI pipeline, the right `.gitignore`, and your org's standard README structure.

## The Problem with Alternatives

If you've tried **cookiecutter** or **copier**, you know they're powerful but have friction:

- Templates live in git repos, making version management manual
- Remote content (your org's standard CI file) means copy-pasting into the template
- No AI integration — you're on your own for keeping templates smart

structkit takes a different approach:

| Feature | cookiecutter | copier | structkit |
|---|---|---|---|
| Remote content (GitHub, S3, GCS, HTTP) | ❌ | ❌ | ✅ |
| AI / MCP integration | ❌ | ❌ | ✅ |
| Pre/post hooks | ✅ | ✅ | ✅ |
| Dry run mode | ❌ | ✅ | ✅ |
| YAML-first (no template repo needed) | ❌ | ❌ | ✅ |
| Multiple file strategies (skip, backup, overwrite) | ❌ | ✅ | ✅ |

## The AI-Native Angle: MCP Integration

The part of structkit that gets developers most excited is the MCP (Model Context Protocol) integration. structkit ships with a built-in MCP server:

```bash
structkit mcp --server
```

This means your AI assistant (Claude, Cursor, Copilot, etc.) can generate project scaffolds directly from natural language:

> "Create a new Terraform module with the standard organization security baseline and a README pre-filled with this module's purpose"

Your templates encode organizational knowledge. The AI executes them. The result is consistent, governed project creation at the speed of conversation.

## Real-World Use Cases

**Platform engineering teams** use structkit to enforce org-wide standards: every new microservice gets the same observability setup, security scanning, and documentation structure — automatically.

**DevEx teams** use structkit to reduce onboarding time for new engineers. Instead of "read the wiki and copy the golden repo," it's `structkit generate service ./my-new-service`.

**Individual developers** use structkit to stop recreating the same boilerplate across side projects — define it once, use it forever.

## Getting Started

```bash
pip install structkit
structkit generate terraform-module ./my-new-module
```

Full documentation: [structkit docs](https://httpdss.github.io/structkit/)

---

*structkit is open source (MIT) and actively developed. Star us on [GitHub](https://github.com/httpdss/structkit) and join the [Discussions](https://github.com/httpdss/structkit/discussions).*
