# AGENTS.md

Guidance for Hermes, Codex, Claude Code, and other AI agents working in this repository.

## Repository

- GitHub repository: `httpdss/structkit`
- Local path: `/home/kenny/development/github.com/httpdss/struct`
- Default branch: `main`
- Standard agent branch prefix for documentation-only changes: `docs/`

## Project Snapshot

- Python project.
- This repo uses Struct metadata in `.struct.yaml`; keep it in sync with structural changes.
README context to preserve:

> # 🚀 StructKit: Automated Project Structure Generator
> ![StructKit Logo](./docs/assets/github-hero.gif)
> [![codecov](https://codecov.io/github/httpdss/structkit/graph/badge.svg?token=JL5WIO1C9T)](https://codecov.io/github/httpdss/structkit)
> ![GitHub issues](https://img.shields.io/github/issues/httpdss/structkit)
> ![GitHub pull requests](https://img.shields.io/github/issues-pr/httpdss/structkit)
> ![GitHub stars](https://img.shields.io/github/stars/httpdss/structkit?style=social)

## Important Files and Directories

- `tests/` — present; inspect before editing related functionality.
- `docs/` — present; inspect before editing related functionality.
- `.github/` — present; inspect before editing related functionality.
- `scripts/` — present; inspect before editing related functionality.
- `structkit/` — present; inspect before editing related functionality.
- `README.md`
- `CONTRIBUTING.md`
- `pyproject.toml`
- `setup.py`
- `requirements.txt`
- `requirements.dev.txt`
- `Dockerfile`
- `.pre-commit-config.yaml`
- `.struct.yaml`

## GitHub Workflows

- `.github/workflows/deploy-pages.yml`
- `.github/workflows/generate-terminal-gifs.yaml`
- `.github/workflows/labeler.yaml`
- `.github/workflows/major-tagging.yaml`
- `.github/workflows/publish-pypi.yml`
- `.github/workflows/push-to-registry.yaml`
- `.github/workflows/release-drafter.yaml`
- `.github/workflows/run_struct.yaml`
- `.github/workflows/struct-generate.yaml`
- `.github/workflows/struct-on-gha.yaml`
- `.github/workflows/test-script.yaml`
- `.github/workflows/z-pre-commit.yaml`

## Safe Agent Workflow

1. Start from a clean checkout of `main` or a fresh worktree based on `origin/main`.
2. Do not overwrite existing user changes. If the working tree is dirty, create a separate worktree for your branch instead of stashing or resetting user work.
3. Create a focused branch, for example `docs/update-agents-md` for agent-instruction changes.
4. Make the smallest targeted change that satisfies the task.
5. Run the most relevant validation command(s) listed below when the touched files affect code, configuration, CI, or generated assets.
6. Commit with a conventional commit message such as `docs: add agent instructions`.
7. Push the branch and open a pull request against `main`.

## Build, Test, and Validation Commands

- `python -m pytest` — run the Python test suite.
- `pre-commit run --all-files` — run configured formatting/lint hooks when available.
- `python -m pip install -r requirements.dev.txt` — install developer dependencies in a virtualenv if needed.

If a command needs dependencies that are not installed, install them in a project-local virtual environment or use the repository's documented devcontainer. Do not install global packages unless the user explicitly asks.

## Editing Guidelines

- Prefer small, reviewable diffs.
- Preserve public APIs, documented command names, workflow inputs, and file paths unless the task explicitly asks to change them.
- Update README or docs when behavior, commands, or configuration changes.
- Keep formatting consistent with nearby files.
- For Markdown-only changes, verify links and headings manually.
- For CI/workflow changes, check YAML syntax and confirm referenced actions, secrets, and inputs still exist.

## Do Not Touch Without Explicit Approval

- `.venv/`
- `__pycache__/`
- coverage output
- credentials, tokens, keys, or private URLs
- secret files such as `.env*`
- Large generated files, vendored dependencies, lockfiles, or build outputs unless the task specifically requires it.
- History-rewriting operations such as `git reset --hard`, force pushes, or deleting branches that may contain user work.

## Security Notes

- Never print, commit, or summarize secret values.
- Treat `.env`, key files, tokens, credentials, cookies, and local config as sensitive.
- If you encounter a secret in tracked files or logs, stop and report it without repeating the value.
- Use placeholders like `[REDACTED]` when discussing sensitive content.

## PR Expectations

- Explain what changed and why.
- Include validation performed, even if it is "not run; documentation-only change".
- Keep PR scope limited to the requested task.
