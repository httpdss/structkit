# Contributing to StructKit

Thank you for your interest in contributing to StructKit! We welcome contributions from the community and are pleased to have you join us.

## 🚀 Quick Start

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** from `main`
4. **Make your changes** and commit them
5. **Push to your fork** and submit a pull request

## 📋 Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A text editor or IDE

### Local Development

Clone the repository:

```bash
git clone https://github.com/httpdss/structkit.git
cd struct
```

Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install in development mode:

```bash
pip install -e .
pip install -r requirements.dev.txt
```

Run tests to ensure everything works:

```bash
pytest
```

## 🔧 Making Changes

### Code Style

- Follow PEP 8 guidelines
- Use 2 spaces for indentation in YAML files
- Use 4 spaces for indentation in Python files
- Write clear, descriptive commit messages
- Add docstrings to new functions and classes

### Testing

- Write tests for new functionality
- Ensure all existing tests pass
- Run the test suite: `pytest`
- Check test coverage: `pytest --cov=structkit`

### Pull Request Guidelines

1. **Create descriptive PR titles** that summarize the change
2. **Fill out the PR template** completely
3. **Link to related issues** when applicable
4. **Keep PRs focused** - one feature/fix per PR
5. **Update documentation** if your changes affect user-facing functionality

## 📝 Documentation

We use Markdown for documentation. When contributing:

- Update relevant documentation files
- Add examples for new features
- Keep language clear and concise
- Follow the existing documentation structure

### Documentation Structure

```text
docs/
├── index.md              # Main documentation index
├── installation.md       # Installation instructions
├── quickstart.md         # Quick start guide
├── configuration.md      # YAML configuration reference
├── template-variables.md # Template variable documentation
├── file-handling.md      # File handling features
├── custom-structures.md  # Creating custom structures
├── hooks.md              # Pre/post hooks
├── mappings.md           # External data mappings
├── github-integration.md # GitHub Actions integration
├── development.md        # Development setup
├── completion.md         # CLI completion setup
├── cli-reference.md      # Complete CLI reference
├── schema.md             # YAML schema reference
├── examples/             # Example configurations
├── articles.md           # External articles and tutorials
├── known-issues.md       # Known limitations
├── contributing.md       # This file
└── funding.md            # Funding information
```

## 🏗️ Contributing New Structures

StructKit includes a collection of contrib structures in `structkit/contribs/`. To add a new structure:

1. **Create a new YAML file** in the appropriate subdirectory
2. **Follow naming conventions**: use lowercase with hyphens
3. **Test your structure** with various scenarios
4. **Add documentation** explaining what the structure does
5. **Include examples** in your PR description

### Structure Guidelines

- Use descriptive file and folder names
- Include appropriate comments in YAML
- Follow the established patterns in existing structures
- Test with different variable combinations
- Ensure compatibility across platforms

## 🐛 Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **OS and Python version**
- **StructKit version** (`structkit --version`)
- **Complete error message** or traceback
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Sample configuration** that reproduces the issue

### Feature Requests

For feature requests:

- **Describe the use case** clearly
- **Explain the benefit** to other users
- **Provide examples** of how it would work
- **Consider implementation complexity**

## 📊 Project Structure

```text
struct/
├── structkit/           # Main Python package
│   ├── commands/           # CLI command implementations
│   ├── contribs/          # Contributed structure templates
│   ├── __init__.py
│   ├── main.py            # CLI entry point
│   ├── file_item.py       # File handling logic
│   ├── template_renderer.py # Jinja2 template rendering
│   ├── content_fetcher.py # Remote content fetching
│   ├── model_wrapper.py   # AI model integration
│   └── utils.py           # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── examples/              # Example configurations
├── requirements.txt       # Production dependencies
├── requirements.dev.txt   # Development dependencies
├── setup.py              # Package configuration
├── struct-schema.json    # JSON schema for validation
└── README.md             # Project overview
```

## 🏷️ Issue Labels

We use labels to categorize issues:

- **`bug`** - Something isn't working
- **`enhancement`** - New feature or request
- **`documentation`** - Improvements to documentation
- **`good first issue`** - Good for newcomers
- **`help wanted`** - Extra attention is needed
- **`question`** - Further information is requested

## 💬 Communication

- **GitHub Issues** - Bug reports and feature requests
- **GitHub Discussions** - General questions and community support
- **Pull Requests** - Code contributions and reviews

## 🙏 Recognition

All contributors will be recognized in our documentation and releases. We appreciate every contribution, whether it's:

- Code improvements
- Bug reports
- Documentation updates
- Feature suggestions
- Community support

## 📜 Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## 🤝 Getting Help

If you need help contributing:

1. Check existing [documentation](index.md)
2. Search [existing issues](https://github.com/httpdss/structkit/issues)
3. Create a new issue with the `question` label
4. Join our [GitHub Discussions](https://github.com/httpdss/structkit/discussions)

Thank you for contributing to StructKit! 🎉
