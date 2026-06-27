# GitHub Actions CI baseline example

Generate a standard GitHub Actions CI workflow plus lightweight project metadata for Python repositories.

## Use case

Use this when you want to apply a consistent CI baseline across internal Python services, CLIs, and libraries.

## Command

```bash
structkit generate --vars "project_name=DemoPythonProject,python_version=3.12" examples/github-actions-ci/.struct.yaml ./demo-ci-baseline
```

## Expected output

- `.github/workflows/ci.yml`
- `.github/dependabot.yml`
- `.pre-commit-config.yaml`
- `README.md`

## Customization notes

- Override `python_version` to match the runtime your organization supports.
- Extend the workflow with package build, coverage upload, or deployment jobs as needed.
