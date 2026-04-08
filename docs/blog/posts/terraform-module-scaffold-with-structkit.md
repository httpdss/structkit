---
title: Building a Terraform Module Scaffold with structkit
date: 2026-04-08
tags:
  - terraform
  - infrastructure-as-code
  - scaffolding
  - devops
authors:
  - httpdss
---

# Building a Terraform Module Scaffold with structkit

> **SEO:** terraform module template generator, infrastructure as code scaffolding

## TL;DR

If you maintain multiple Terraform modules, you know the pain: every new module starts with copy-pasting the same `main.tf`, `variables.tf`, `outputs.tf`, and `.github/` setup. [structkit](https://github.com/httpdss/structkit) lets you define that structure once in YAML and generate it consistently across your team.

<!-- more -->

## The Problem: Terraform Module Sprawl

As your infrastructure grows, so does your module library. Two things are always true:

1. **New modules start with copy-paste** — someone grabs an old module and strips it down
2. **Consistency degrades over time** — modules end up with different structures, naming conventions, CI configurations

This causes real pain:
- Onboarding engineers spend hours understanding why Module A has a `providers.tf` but Module B does not
- Security reviews find inconsistent IAM patterns across modules
- CI pipelines fail because some modules have `terratest`, others do not

## What structkit Does

structkit is a YAML-first scaffolding tool that generates project structures from templates. You define the shape of a project once and structkit materializes it.

```bash
pip install structkit
```

## Scaffolding a Terraform Module

Here is a complete `structkit.yaml` for a standard Terraform module:

```yaml
structure:
  - name: "{{module_name}}"
    type: directory
    children:
      - name: main.tf
        type: file
        content: |
          # {{module_name}} -- {{module_description}}
          terraform {
            required_version = ">= 1.5"
            required_providers {
              aws = {
                source  = "hashicorp/aws"
                version = "~> 5.0"
              }
            }
          }

      - name: variables.tf
        type: file
        content: |
          variable "name" {
            description = "Name prefix for all resources"
            type        = string
          }

      - name: outputs.tf
        type: file
        content: |
          # Add module outputs here

      - name: README.md
        type: file
        content: |
          # {{module_name}}
          {{module_description}}

          ## Usage
          module "{{module_name}}" {
            source = "./{{module_name}}"
            name   = "my-resource"
          }

      - name: .github/workflows/terraform.yml
        type: file
        content: |
          name: Terraform
          on:
            pull_request:
              branches: [main]
          jobs:
            validate:
              runs-on: ubuntu-latest
              steps:
                - uses: actions/checkout@v4
                - uses: hashicorp/setup-terraform@v3
                - run: terraform init -backend=false
                - run: terraform validate
                - run: terraform fmt -check
```

## Generating the Module

```bash
structkit generate \
  --config structkit.yaml \
  --var module_name=aws-s3-bucket \
  --var module_description="Opinionated S3 bucket module with versioning and encryption"
```

Output:

```
aws-s3-bucket/
├── main.tf
├── variables.tf
├── outputs.tf
├── README.md
└── .github/workflows/terraform.yml
```

Every module your team creates has the same CI setup, the same pre-commit hooks, the same README structure.

## Remote Templates

structkit supports remote content fetching. Host your template in a central Git repo:

```yaml
structure:
  remote: https://github.com/yourorg/structkit-templates/terraform-module/structkit.yaml
```

Now any engineer can scaffold a compliant module without knowing the internal structure:

```bash
structkit generate \
  --remote https://github.com/yourorg/structkit-templates/terraform-module/structkit.yaml \
  --var module_name=aws-rds-postgres
```

## Team-Wide Standardization

Store templates in a central repository:

```
yourorg/structkit-templates/
├── terraform-module/structkit.yaml
├── terraform-root/structkit.yaml
├── python-service/structkit.yaml
└── github-action/structkit.yaml
```

Platform teams own the templates. Product teams consume them. Everyone gets consistency without a manual review process.

## Comparing Approaches

| Approach | Consistency | Learning curve |
|---|---|---|
| Manual copy-paste | Degrades over time | Very low |
| cookiecutter | Good | Medium |
| copier | Good (with updates) | Medium-high |
| structkit | Good | Low (just YAML) |

structkit is YAML-first. If you can write YAML (which you already do for Terraform), you can write structkit templates.

## What is Next

- **AI/MCP integration**: structkit supports Claude MCP for natural-language scaffolding
- **GitHub Actions**: run structkit in CI to enforce that new modules follow templates

## Get Started

```bash
pip install structkit
```

- GitHub: [httpdss/structkit](https://github.com/httpdss/structkit)
- PyPI: [structkit](https://pypi.org/project/structkit/)

---

*Did this help? Star [httpdss/structkit](https://github.com/httpdss/structkit) and share your use case in the comments!*
