# 🚀 StructKit: Automated Project Structure Generator

![StructKit Logo](./docs/assets/github-hero.gif)

[![codecov](https://codecov.io/github/httpdss/structkit/graph/badge.svg?token=JL5WIO1C9T)](https://codecov.io/github/httpdss/struct)
![GitHub issues](https://img.shields.io/github/issues/httpdss/struct)
![GitHub pull requests](https://img.shields.io/github/issues-pr/httpdss/struct)
![GitHub stars](https://img.shields.io/github/stars/httpdss/struct?style=social)

**StructKit** is a powerful, flexible tool for automating project structure creation through YAML configurations. Generate consistent project layouts, boilerplate code, and configurations with template variables, remote content fetching, and intelligent file handling.

> 📚 **[View Complete Documentation](docs/index.md)** | 🚀 **[Quick Start Guide](docs/quickstart.md)** | 🔧 **[Installation](docs/installation.md)**

## ✨ Key Features

- **📝 YAML-Based Configuration** - Define project structures in simple, readable YAML
- **🔧 Template Variables** - Dynamic content with Jinja2 templating and interactive prompts
- **🌐 Remote Content** - Fetch files from GitHub, HTTP/HTTPS, S3, and Google Cloud Storage
- **🛡️ Smart File Handling** - Multiple strategies for managing existing files (overwrite, skip, backup, etc.)
- **🪝 Automation Hooks** - Pre and post-generation shell commands
- **🎯 Dry Run Mode** - Preview changes before applying them
- **✅ Validation & Schema** - Built-in YAML validation and IDE support
- **🤖 MCP Integration** - Model Context Protocol support for AI-assisted development workflows

## 🚀 Quick Start

### Installation

```bash
# Install via pip
pip install structkit

# Or run with Docker
docker run -v $(pwd):/workdir ghcr.io/httpdss/structkit:main generate my-config.yaml ./output
```

### Basic Usage

```bash
# Generate a Terraform module structure
structkit generate terraform-module ./my-terraform-module

# List available structures
structkit list

# Validate a configuration
structkit validate my-config.yaml

# Start MCP server for AI integration
structkit mcp --server
 ```

### Example Configuration

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}
        Generated with StructKit
  - .gitignore:
      file: github://github/gitignore/main/Python.gitignore

folders:
  - src/:
      struct: project/python
      with:
        app_name: "{{@ project_name | slugify @}}"

variables:
  - project_name:
      description: "Name of your project"
      type: string
      default: "MyProject"
```

## 📚 Documentation

Our comprehensive documentation is organized into the following sections:

### 🏁 Getting Started

- **[Installation Guide](docs/installation.md)** - Multiple installation methods
- **[Quick Start](docs/quickstart.md)** - Get up and running in minutes
- **[Basic Usage](docs/usage.md)** - Core commands and options

### ⚙️ Configuration

- **[YAML Configuration](docs/configuration.md)** - Complete configuration reference
- **[Template Variables](docs/template-variables.md)** - Dynamic content and Jinja2 features
- **[File Handling](docs/file-handling.md)** - Managing files, permissions, and remote content
- **[Schema Reference](docs/schema.md)** - YAML validation and IDE support

### 🔧 Advanced Features

- **[Hooks](docs/hooks.md)** - Pre and post-generation automation
- **[Mappings](docs/mappings.md)** - External data integration
- **[GitHub Integration](docs/github-integration.md)** - Automation with GitHub Actions
- **[MCP Integration](docs/mcp-integration.md)** - Model Context Protocol for AI-assisted workflows
- **[Command-Line Completion](docs/completion.md)** - Enhanced CLI experience

### 👩‍💻 Development

- **[Development Setup](docs/development.md)** - Contributing to StructKit
- **[Known Issues](docs/known-issues.md)** - Current limitations and workarounds

### 📖 Resources

- **[Articles & Tutorials](docs/articles.md)** - Community content and learning resources
- **[Examples](example/)** - Practical examples and use cases

## 🎯 Use Cases

- **Infrastructure as Code** - Generate Terraform modules, Kubernetes manifests
- **Application Scaffolding** - Bootstrap microservices, APIs, frontend projects
- **DevOps Automation** - CI/CD pipeline templates, configuration management
- **Documentation** - Consistent project documentation and compliance templates

## 🤝 Community

- **[Contributing Guidelines](docs/development.md#contributing-guidelines)** - How to contribute
- **[GitHub Discussions](https://github.com/httpdss/structkit/discussions)** - Community support
- **[Articles & Tutorials](docs/articles.md)** - Learning resources

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 💰 Support

If StructKit helps your workflow, consider supporting the project: [patreon/structproject](https://patreon.com/structproject)

---

**📚 [Complete Documentation](docs/index.md)** | **🐛 [Report Issues](https://github.com/httpdss/structkit/issues)** | **💬 [Discussions](https://github.com/httpdss/structkit/discussions)**
