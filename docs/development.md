# Development Setup

This guide will help you set up a development environment for contributing to StructKit.

## Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, virtualenv, or conda)

## Getting Started

### 1. Clone the Repository

```sh
git clone https://github.com/httpdss/structkit.git
cd struct
```

### 2. Create a Virtual Environment

```sh
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```sh
# Install runtime dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements.dev.txt

# Install the package in development mode
pip install -e .
```

### 4. Verify Installation

```sh
structkit --help
```

## Development Workflow

### Running Tests

```sh
# Run all tests
pytest

# Run tests with coverage
pytest --cov=structkit

# Run specific test file
pytest tests/test_specific.py
```

### Code Quality

This project uses several tools to maintain code quality:

```sh
# Format code with black
black .

# Sort imports
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy structkit/
```

### Pre-commit Hooks

Install pre-commit hooks to automatically run quality checks:

```sh
pre-commit install
```

This will run formatting, linting, and tests before each commit.

## Project Structure

```text
struct/
├── structkit/          # Main Python package
│   ├── commands/          # CLI command implementations
│   ├── contribs/          # Built-in structure templates
│   └── ...
├── tests/                 # Test files
├── docs/                  # Documentation
├── example/               # Example configurations
├── scripts/               # Utility scripts
└── requirements*.txt      # Dependencies
```

## Adding New Features

### 1. Create a New Command

Commands are defined in `structkit/commands/`. Each command should:

- Inherit from a base command class
- Include proper argument parsing
- Have comprehensive tests
- Include documentation

Example:

```python
# structkit/commands/my_command.py
from .base import BaseCommand

class MyCommand(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--option', help='My option')

    def handle(self, args):
        # Implementation here
        pass
```

### 2. Add Structure Templates

New structure templates go in `structkit/contribs/`. Each template should:

- Have a clear directory structure
- Provide good documentation
- Include example usage

### 3. Write Tests

All new functionality must include tests:

```python
# tests/test_my_feature.py
import pytest
from structkit.my_feature import MyFeature

def test_my_feature():
    feature = MyFeature()
    result = feature.do_something()
    assert result == expected_value
```

### 4. Update Documentation

- Add or update relevant documentation in `docs/`
- Add examples if applicable

## Testing

### Unit Tests

Run unit tests to verify individual components:

```sh
pytest tests/unit/
```

### Integration Tests

Run integration tests to verify end-to-end functionality:

```sh
pytest tests/integration/
```

## Debugging

### Enable Debug Logging

```sh
structkit --log=DEBUG generate my-config.yaml ./output
```

### Use Python Debugger

Add breakpoints in your code:

```python
import pdb; pdb.set_trace()
```

```sh
structkit --log=DEBUG generate my-config.yaml ./output
```

## Contributing Guidelines

### Code Style

- Follow PEP 8
- Use type hints where appropriate
- Write docstrings for public functions
- Keep functions small and focused

### Commit Messages

Use conventional commit format:

```text
feat: add new template variable filter
fix: resolve issue with file permissions
docs: update installation guide
test: add tests for mappings functionality
```

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Write tests
5. Update documentation
6. Submit a pull request

### Review Process

All pull requests must:

- Pass all tests
- Include appropriate documentation
- Follow code style guidelines
- Have a clear description of changes

## Troubleshooting

### Common Issues

**Import errors**: Make sure you've installed the package in development mode:

```sh
pip install -e .
```

**Test failures**: Ensure all dependencies are installed:

```sh
pip install -r requirements.dev.txt
```

**Permission errors**: Check file permissions and ensure you're in the right directory.

### Getting Help

- Check existing issues on GitHub
- Join our Discord community
- Read the documentation thoroughly
- Ask questions in discussions

## Resources

- [Python Development Guide](https://docs.python.org/3/tutorial/)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)
- [Conventional Commits](https://www.conventionalcommits.org/)
