# 🚀 StructKit: YAML-first scaffolding for teams and AI agents

> Define project structures once in YAML, then generate consistent repos, CI files, docs, Terraform modules, and app layouts locally, in CI, or through an AI assistant via MCP.

![StructKit demo: generate project structure from YAML](./docs/assets/github-hero.gif)

[![codecov](https://codecov.io/github/httpdss/structkit/graph/badge.svg?token=JL5WIO1C9T)](https://codecov.io/github/httpdss/structkit)
![GitHub issues](https://img.shields.io/github/issues/httpdss/structkit)
![GitHub pull requests](https://img.shields.io/github/issues-pr/httpdss/structkit)
![GitHub stars](https://img.shields.io/github/stars/httpdss/structkit?style=social)

**StructKit** replaces copy-pasted boilerplate and aging "golden repos" with reusable YAML structures. It can render template variables, fetch canonical files from remote sources, preview changes before writing, and expose your scaffolds to AI assistants through the Model Context Protocol.

> 🚀 **[Quick Start](docs/quickstart.md)** | 📚 **[Docs](docs/index.md)** | 🧩 **[Examples](examples/)** | 🤖 **[MCP / AI Agent Guide](docs/mcp-integration.md)** | 🧠 **[Agent Skills](docs/agent-skills.md)** | 💬 **[Discussions](https://github.com/httpdss/structkit/discussions)**

## ⚡ Try it in 60 seconds

```bash
# Install the CLI
pip install structkit

# Preview available bundled structures
structkit list

# Generate a ready-made Terraform module scaffold
structkit generate --vars module_name=my-terraform-module terraform/modules/generic ./my-terraform-module
```

Prefer Docker?

```bash
docker run --rm -v "$(pwd):/workdir" ghcr.io/httpdss/structkit:main \
  generate --vars module_name=my-terraform-module terraform/modules/generic ./my-terraform-module
```

## 👤 Who StructKit is for

- **Platform / DevEx teams** standardizing service layouts, CI baselines, and engineering conventions across many repos.
- **DevOps engineers** generating repeatable Terraform modules, Kubernetes manifests, GitHub Actions workflows, and config bundles.
- **AI coding workflow users** who want assistants to scaffold from approved templates instead of inventing project structure.
- **Individual developers** tired of rebuilding the same files, folders, and docs for every new project.

## 🤔 Why StructKit?

Project scaffolding tools exist in most ecosystems, but StructKit solves problems the others often leave to copy-paste, template repositories, or custom scripts.

| Feature | cookiecutter | copier | **StructKit** |
|---|---|---|---|
| Remote content (GitHub, S3, GCS, HTTP) | ❌ | ❌ | ✅ |
| AI / MCP integration | ❌ | ❌ | ✅ |
| Pre/post generation hooks | ✅ | ✅ | ✅ |
| Dry run mode | ❌ | ✅ | ✅ |
| YAML-first (no template repo required) | ❌ | ❌ | ✅ |
| Multiple file conflict strategies | ❌ | ✅ | ✅ |
| IDE schema validation | ❌ | ❌ | ✅ |

**Key differentiators:**

- **Remote-first content:** Reference your organization's canonical CI template from GitHub directly in your StructKit config. When the template updates, all new projects get the update — no copy-paste maintenance.
- **AI-native via MCP:** Start the StructKit MCP server so your AI assistant can generate project scaffolds from natural language using your templates as the source of truth.
- **Agent skill ready:** Install the companion [`httpdss/structkit-skills`](https://github.com/httpdss/structkit-skills) workflow skill so AI assistants consistently inspect, preview, generate, and validate StructKit structures.
- **YAML-first:** Define structures directly in YAML. No separate template repository is required.
- **Safe by default:** Use dry-run previews and file conflict strategies before writing into existing projects.

## ✨ Key Features

- **📝 YAML-Based Configuration** - Define project structures in simple, readable YAML
- **🔧 Template Variables** - Dynamic content with Jinja2 templating and interactive prompts
- **🌐 Remote Content** - Fetch files from GitHub, HTTP/HTTPS, S3, and Google Cloud Storage
- **🛡️ Smart File Handling** - Multiple strategies for managing existing files (overwrite, skip, backup, etc.)
- **🪝 Automation Hooks** - Pre and post-generation shell commands
- **🎯 Dry Run Mode** - Preview changes before applying them
- **✅ Validation & Schema** - Built-in YAML validation and IDE support
- **🤖 MCP Integration** - Model Context Protocol support for AI-assisted development workflows

## 🚀 More usage examples

```bash
# Generate a Terraform module structure
structkit generate --vars module_name=my-terraform-module terraform/modules/generic ./my-terraform-module

# List available structures
structkit list

# Validate a configuration
structkit validate my-config.yaml

# Start MCP server for AI integration
structkit mcp --server
```

If StructKit saves you setup time, **star the repo**, try an [example](examples/), or share your use case in [GitHub Discussions](https://github.com/httpdss/structkit/discussions).

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
- **[MCP / AI Agent Workflow](docs/mcp-integration.md)** - Model Context Protocol for approved-template scaffolding with AI assistants
- **[Agent Skills](docs/agent-skills.md)** - Installable StructKit workflow skill for AI assistants
- **[Command-Line Completion](docs/completion.md)** - Enhanced CLI experience

### 👩‍💻 Development

- **[Development Setup](docs/development.md)** - Contributing to StructKit
- **[Known Issues](docs/known-issues.md)** - Current limitations and workarounds

### 📖 Resources

- **[Articles & Tutorials](docs/articles.md)** - Community content and learning resources
- **[Examples](examples/)** - Practical examples and use cases

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
