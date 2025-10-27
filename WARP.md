# WARP.md - StructKit Project Guide

> This file serves as a comprehensive guide for developers working with the StructKit project. It contains project-specific conventions, development workflows, and institutional knowledge.

## 🎯 Project Overview

### Mission

StructKit simplifies project organization by creating consistent file and folder structures tailored to specific needs. It enhances productivity and maintains uniformity across projects through YAML-based configuration files.

### Key Features

- **YAML-Based Configuration**: Simple, readable project structure definitions
- **Template Variables**: Dynamic content with Jinja2 templating and interactive prompts
- **Remote Content Fetching**: Support for GitHub, HTTP/HTTPS, S3, and Google Cloud Storage
- **Smart File Handling**: Multiple strategies for managing existing files
- **Automation Hooks**: Pre and post-generation shell commands
- **MCP Integration**: Model Context Protocol support for AI-assisted workflows

### Technology Stack

- **Language**: Python 3.12+
- **CLI Framework**: argparse with custom command pattern
- **Templating**: Jinja2 with custom delimiters
- **Testing**: pytest with coverage reporting
- **Documentation**: MkDocs with Material theme
- **CI/CD**: GitHub Actions
- **Package Management**: pip with requirements.txt

## 🛠 Development Environment

### Prerequisites

```bash
# Python 3.12 or higher
python --version

# Virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements.dev.txt
```

### Environment Variables

```bash
# Optional: OpenAI API key for AI features
export OPENAI_API_KEY="your-api-key-here"

# Optional: GitHub token for private repo access
export GITHUB_TOKEN="your-github-token"

# Optional: Logging level
export STRUCTKIT_LOG_LEVEL="DEBUG"
```

### IDE Configuration

- **VS Code**: Recommended extensions in `.vscode/extensions.json`
- **PyCharm**: Python interpreter should point to `.venv/bin/python`
- **Pre-commit hooks**: Run `pre-commit install` after setup

## 🏗 Code Structure

### Directory Layout

```text
structkit/
├── commands/           # CLI command implementations
│   ├── generate.py    # Main generation command
│   ├── validate.py    # YAML validation
│   ├── list.py        # List available structures
│   └── ...
├── contribs/          # Built-in structure templates
├── filters.py         # Jinja2 custom filters
├── template_renderer.py  # Core templating logic
├── file_item.py       # File handling and processing
├── input_store.py     # User input persistence
├── utils.py           # Utility functions
└── main.py           # Entry point

tests/                 # Test suite
docs/                  # Documentation source
examples/              # Example configurations
```

### Key Modules

#### `template_renderer.py`

- Handles Jinja2 templating with custom delimiters
- Interactive variable prompting with descriptions
- Type coercion and validation
- Icon-based user interface

#### `file_item.py`

- Represents files to be created/modified
- Handles different content sources (inline, remote, etc.)
- Implements file creation strategies (overwrite, skip, backup, etc.)

#### `commands/`

- Each command is a separate class inheriting from `Command`
- Self-contained argument parsing and execution logic
- Consistent error handling and logging

## 🔄 Development Workflow

### Branch Strategy

- `main`: Production-ready code
- `feature/*`: New features (e.g., `feature/display-variable-descriptions-116`)
- `bugfix/*`: Bug fixes
- `hotfix/*`: Critical production fixes
- `docs/*`: Documentation updates

### Commit Message Convention

```text
<type>(<scope>): <description>

<body>

<footer>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:

```text
feat(template): add variable description display in interactive mode
fix(file-handling): resolve path resolution on Windows
docs(api): update template variables documentation
```

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation if needed
4. Run full test suite: `pytest tests/`
5. Check code style: `pre-commit run --all-files`
6. Create PR with descriptive title and body
7. Link related issues: "Closes #123"
8. Request review from maintainers

## 🧪 Testing Guidelines

### Test Structure

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=structkit --cov-report=html

# Run specific test file
pytest tests/test_template_renderer.py -v

# Run specific test
pytest tests/test_template_renderer.py::test_prompt_with_description_display -v
```

### Test Categories

- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component functionality
- **Command Tests**: CLI command end-to-end testing
- **Template Tests**: YAML configuration validation

### Test Data

- Test fixtures in `tests/fixtures/`
- Mock objects for external dependencies
- Temporary files in `/tmp/` for file system tests

### Coverage Goals

- Minimum 85% line coverage
- All new features must include tests
- Critical paths require 100% coverage

## 📝 Code Style & Standards

### Python Style

- **PEP 8** compliance with line length of 100 characters
- **Type hints** for all public functions
- **Docstrings** for all modules, classes, and public functions
- **F-strings** for string formatting

### Code Quality Tools

```bash
# Linting
flake8 structkit/

# Type checking
mypy structkit/

# Pre-commit hooks (automated)
pre-commit run --all-files
```

### Variable Naming

- `snake_case` for variables and functions
- `UPPER_CASE` for constants
- Descriptive names over abbreviations
- Prefix private methods with underscore

### Error Handling

- Use specific exception types
- Provide helpful error messages
- Log errors with appropriate levels
- Clean up resources in finally blocks

## 🚀 Release Process

### Version Numbering

- Semantic versioning: `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features, backward compatible
- `PATCH`: Bug fixes

### Release Checklist

1. Update `CHANGELOG.md`
2. Bump version in `setup.py`
3. Run full test suite
4. Update documentation
5. Create release PR
6. Tag release: `git tag v1.2.3`
7. GitHub Actions handles PyPI publication

### Release Notes

- Categorize changes: Added, Changed, Fixed, Removed
- Include migration notes for breaking changes
- Reference GitHub issues and PRs
- Highlight security fixes

## 🔧 Common Tasks

### Adding a New Command

1. Create new file in `structkit/commands/`
2. Inherit from `Command` base class
3. Implement `__init__` with argument parsing
4. Implement `execute` method
5. Add command to `main.py`
6. Add tests in `tests/test_commands.py`

### Adding New Template Filters

1. Implement filter function in `structkit/filters.py`
2. Add to `custom_filters` dict in `template_renderer.py`
3. Document in `docs/template-variables.md`
4. Add tests in `tests/test_filters.py`

### Creating Built-in Structures

1. Create YAML file in `structkit/contribs/`
2. Follow naming convention: `project-type.yaml`
3. Include comprehensive variable definitions
4. Add example in `docs/examples/`
5. Update `structkit list` output

## 🐛 Troubleshooting

### Common Issues

#### Template Variables Not Resolving

- Check custom delimiters: `{{@` `@}}`
- Verify variable names match configuration
- Check for typos in YAML structure

#### File Creation Failures

- Verify file permissions
- Check disk space
- Validate file paths (no invalid characters)
- Review file strategy settings

#### Import Errors

- Ensure virtual environment is activated
- Check Python version compatibility
- Verify all dependencies installed: `pip install -r requirements.txt`

### Debug Mode

```bash
# Enable debug logging
export STRUCTKIT_LOG_LEVEL=DEBUG
structkit generate config.yaml --log DEBUG

# Dry run mode for testing
structkit generate config.yaml ./output --dry-run

# Console output for inspection
structkit generate config.yaml --output console
```

### Log Analysis

- Logs include timestamps and severity levels
- File operations logged with full paths
- Template rendering logged with variable values
- Error stack traces include line numbers

## 🏛 Architecture Decisions

### Template Engine Choice (Jinja2)

- **Decision**: Use Jinja2 with custom delimiters
- **Rationale**: Mature, well-documented, powerful
- **Trade-offs**: Custom delimiters prevent YAML conflicts
- **Date**: 2024-07-11

### Command Pattern Implementation

- **Decision**: Each CLI command is a separate class
- **Rationale**: Modular, testable, extensible
- **Trade-offs**: Slightly more boilerplate
- **Date**: 2024-07-15

### File Strategy System

- **Decision**: Pluggable file handling strategies
- **Rationale**: Flexibility for different use cases
- **Trade-offs**: Increased complexity
- **Date**: 2024-08-01

## ⚡ Performance Considerations

### Template Rendering

- Templates compiled once and cached
- Variable resolution optimized for common cases
- Large files streamed rather than loaded in memory

### File Operations

- Batch operations where possible
- Minimal filesystem stat calls
- Progress indicators for long operations

### Memory Usage

- File contents not held in memory unnecessarily
- Generator patterns for large datasets
- Proper cleanup of temporary resources

## 🔐 Security Guidelines

### Input Validation

- All user inputs validated and sanitized
- Path traversal protection in file operations
- YAML parsing with safe loader only

### External Content

- HTTPS required for remote content
- Validate SSL certificates
- Timeout limits for network operations
- Size limits for downloaded content

### Secrets Handling

- Never log sensitive information
- Environment variables for API keys
- Mask secrets in error messages
- Clear sensitive data from memory

## 📚 Documentation Standards

### Code Documentation

- Docstrings follow Google style
- Type hints for all parameters and returns
- Examples in docstrings for complex functions
- Inline comments for non-obvious logic

### User Documentation

- Step-by-step tutorials with examples
- Reference documentation for all features
- Troubleshooting guides with common solutions
- Migration guides for breaking changes

### API Documentation

- Auto-generated from docstrings
- Include usage examples
- Document exceptions and error conditions
- Keep in sync with code changes

## 📦 Dependencies & Tools

### Core Dependencies

- `Jinja2`: Template engine
- `PyYAML`: YAML parsing
- `requests`: HTTP client
- `boto3`: AWS S3 integration
- `google-cloud-storage`: GCS integration

### Development Dependencies

- `pytest`: Testing framework
- `coverage`: Code coverage
- `flake8`: Linting
- `pre-commit`: Git hooks
- `mkdocs`: Documentation

### Optional Dependencies

- `openai`: AI integration
- `anthropic`: Claude integration
- `fastapi`: MCP server support

### Dependency Management

- Pin major versions in `requirements.txt`
- Regular security updates
- Remove unused dependencies
- Document version constraints

## 📊 Monitoring & Observability

### Metrics Collection

- Command execution times
- File operation success rates
- Template rendering performance
- Error rates by category

### Logging Strategy

- Structured logging with JSON format
- Different log levels for different audiences
- Correlation IDs for tracing requests
- Log rotation and retention policies

### Health Checks

- Basic functionality verification
- External service connectivity
- Resource availability checks
- Performance regression detection

## 🐙 Issue & Work Management

### GitHub MCP for Issues

This project uses **GitHub** for issue tracking and work management. All issue-related queries and work management should use the GitHub MCP tools, **not Jira**.

### Common GitHub MCP Operations

#### List Issues

```bash
# Use the GitHub MCP to list all open issues
list_issues owner:httpdss repo:structkit state:open
```

#### Get Issue Details

```bash
# Get details for a specific issue number
get_issue owner:httpdss repo:structkit issue_number:100
```

#### Create an Issue

```bash
# Create a new issue
create_issue owner:httpdss repo:structkit title:"Issue Title" body:"Issue description"
```

#### Search Issues

```bash
# Search for issues by keyword or status
search_issues query:"keyword" owner:httpdss repo:struct
```

### Issue Workflow

1. **Browse Issues**: Use `list_issues` to see current open issues
2. **Get Details**: Use `get_issue` to understand specific issue requirements
3. **Comment**: Use `add_issue_comment` to provide updates
4. **Link PRs**: Use "Closes #123" in pull requests to link them to issues

---

## 📝 Notes & TODOs

### Future Enhancements

- [ ] Plugin system for custom commands
- [ ] GUI interface for non-technical users
- [ ] Integration with more cloud providers
- [ ] Advanced template debugging tools
- [ ] Performance profiling dashboard

### Known Limitations

- Large file handling could be optimized
- Windows path handling has edge cases
- Some template features not well documented
- MCP integration is still experimental

---

*This document is living documentation. Please update it as the project evolves.*

**Last Updated**: 2025-09-22
**Version**: 1.0
**Maintainer**: Kenneth Belitzky (@httpdss)
