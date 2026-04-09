---
title: "Scaffold Any Project with Natural Language: structkit + MCP"
date: 2026-04-22
tags:
  - mcp
  - ai
  - scaffolding
  - platform-engineering
  - claude
authors:
  - httpdss
---

structkit now integrates with the Model Context Protocol (MCP). You can scaffold entire project structures just by describing what you want to Claude. No memorizing CLI flags, no reading docs — just describe the project and it appears.

<!-- more -->

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io) (MCP) is an open standard from Anthropic that lets AI assistants like Claude call external tools. Instead of typing commands, you describe what you want and Claude handles the tooling.

structkit ships with MCP support out of the box.

## Setup

Install structkit:

```bash
pip install structkit
```

Add it to your Claude MCP config (`~/.claude/mcp.json` or your Claude Desktop config):

```json
{
  "mcpServers": {
    "structkit": {
      "command": "structkit",
      "args": ["mcp"]
    }
  }
}
```

Restart Claude and structkit tools are now available.

## Example: Scaffold a Python Service

Instead of:

```bash
structkit generate \
  --config https://github.com/myorg/templates/python-service.yaml \
  --var service_name=auth-service \
  --var port=8080 \
  --var database=postgres
```

You say to Claude:

> "Create a new Python FastAPI service called auth-service, port 8080, PostgreSQL database, with Docker support"

Claude calls structkit, which generates the full project structure. You see the result appear in your filesystem.

## Example: Terraform Module

> "Scaffold a Terraform module for an AWS S3 bucket with versioning and encryption enabled"

Result:

```
aws-s3-bucket/
├── main.tf       (with versioning + encryption resources)
├── variables.tf  (name, bucket_name, tags)
├── outputs.tf    (bucket_arn, bucket_id)
├── README.md     (auto-generated docs)
└── .github/workflows/terraform.yml
```

## What structkit Actually Does

structkit is not an AI tool — it is a YAML-first scaffolding engine. MCP is just the interface. Under the hood:

1. You describe what you want
2. Claude selects or constructs the right structkit template
3. structkit generates files deterministically from that template
4. You get real, editable code — not AI-hallucinated code

This matters because your scaffolded project is a structkit template output, not a one-shot AI generation. It is **reproducible, auditable, and follows your organization's standards**.

## The Platform Engineering Use Case

For platform teams, this is the real unlock:

1. Platform team maintains structkit templates (Python service, Go service, Terraform module, etc.)
2. Product teams use Claude + MCP to scaffold new projects
3. Every project starts from an approved, standardized template
4. No copy-paste drift, no "I forgot to add the security scanning step"

Developers get natural-language UX. Platform teams get compliance.

## Try It

```bash
pip install structkit
structkit mcp  # start the MCP server
```

- GitHub: [httpdss/structkit](https://github.com/httpdss/structkit)
- Docs: [MCP Integration](https://httpdss.github.io/structkit/mcp-integration/)
- Questions: [GitHub Discussions](https://github.com/httpdss/structkit/discussions)

---

**Read more:** [Consistent Project Scaffolding at Scale with structkit](../consistent-project-scaffolding-with-structkit.md) | [structkit vs cookiecutter vs copier](../structkit-vs-cookiecutter-vs-copier.md)

---

*structkit is open source (MIT). Contributions and template shares welcome.*
