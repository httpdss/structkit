# Contributing to structkit

Thank you for your interest in contributing! structkit is a YAML-first project scaffolding tool for platform engineering teams, and community contributions are what make it better.

## Ways to Contribute

- **Report bugs** — [open a bug report](.github/ISSUE_TEMPLATE/bug_report.md)
- **Request features** — [open a feature request](.github/ISSUE_TEMPLATE/feature_request.md)
- **Share your templates** — post in [GitHub Discussions](https://github.com/httpdss/structkit/discussions)
- **Fix bugs or implement features** — see the workflow below
- **Improve docs** — typos, examples, tutorials all welcome

## Development Setup

```bash
# Clone the repo
git clone https://github.com/httpdss/structkit.git
cd structkit

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Running Tests

```bash
pytest
```

To run a specific test file:

```bash
pytest tests/test_generate.py -v
```

## Submitting a Pull Request

1. **Fork** the repo and create a branch from `main`
2. **Make your changes** — keep PRs focused; one feature or fix per PR
3. **Add tests** — new behavior should have test coverage
4. **Run pre-commit** — `pre-commit run --all-files`
5. **Open a PR** — describe what you changed and why

PR title format: `type: short description` (e.g. `feat: add remote template caching`, `fix: handle empty YAML files`)

## Template Contributions

Have a useful structkit template? The best place to share it is [GitHub Discussions → Show your structkit templates](https://github.com/httpdss/structkit/discussions). If it's broadly useful, we may feature it in the docs.

## Code Style

- Python 3.9+
- Black formatting (enforced by pre-commit)
- Type hints encouraged for new code
- Docstrings for public functions

## Questions?

Open a [GitHub Discussion](https://github.com/httpdss/structkit/discussions) — we're happy to help.
