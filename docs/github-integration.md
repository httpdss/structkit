# GitHub Integration

StructKit can seamlessly integrate with GitHub to automate the generation of project structures across repositories.

## Automating StructKit

Combine GitHub Actions with StructKit to automate project structure generation in CI/CD pipelines. Trigger the process manually or automatically based on events like pull requests or pushes.

Example Workflow:

```yaml
name: run-struct

on:
  workflow_dispatch:

jobs:
  generate:
    uses: httpdss/structkit/.github/workflows/struct-generate.yaml@main
    secrets:
      token: ${{ secrets.STRUCT_RUN_TOKEN }}
```

When `struct_file` is omitted, the workflow uses `.structkit.yaml` if present and falls back to a legacy `.struct.yaml`.

## GitHub Action step (`httpdss/structkit-action`)

For validate, generate, or a dry-run diff/drift check **as a step** in your own job (instead of calling the reusable workflow as a complete job), use [`httpdss/structkit-action`](https://github.com/httpdss/structkit-action).

Validate:

```yaml
- uses: actions/checkout@v7
- uses: httpdss/structkit-action@v1
  with:
    command: validate
    struct_file: .structkit.yaml
```

Drift check (`generate` + `--dry-run --diff`):

```yaml
- uses: httpdss/structkit-action@v1
  with:
    command: generate
    struct_file: .structkit.yaml
    dry_run: true
    diff: true
    fail_on_diff: true
```

Generate:

```yaml
- uses: httpdss/structkit-action@v1
  with:
    command: generate
    struct_file: .structkit.yaml
    output_dir: .
```

The reusable workflow above is a full job with built-in PR creation. The action is a step you can mix with other checkout, test, or commit steps. See the [action README](https://github.com/httpdss/structkit-action) for full workflow examples and inputs.

## Best Practices

1. **Secure Your Token**: Store GitHub tokens in secrets management tools.
2. **Use Topics for Filtering**: Organize repositories with topics to efficiently manage workflows.
3. **Test Locally First**: Simulate script actions with `--dry-run` before executing in a CI/CD environment.
4. **Combine with Other Tools**: Use StructKit with Terraform, Ansible, or Docker for comprehensive project management.

## FAQs

### Why use a GitHub Integration?

Using GitHub integration allows you to leverage StructKit's automation capabilities in a version-controlled environment, enabling consistent and repeatable project structures.

### Can I customize the GitHub Action?

Yes, you can tailor the GitHub Action to your specific needs, including custom triggers, different environments, and additional dependencies.
