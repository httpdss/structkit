# StructKit VHS Demo Tapes

This directory contains [VHS](https://github.com/charmbracelet/vhs) tape files for creating animated GIF demonstrations of StructKit's features. These tapes showcase various use cases and capabilities of the StructKit tool.

## 🎬 Available Tapes

### 1. Installation & Setup

**File**: `install.tape`
**Duration**: ~30 seconds
**Description**: Shows how to install StructKit using pip and verify the installation.

### 2. Basic Usage

**File**: `basic-usage.tape`
**Description**: Demonstrates basic StructKit commands like `list`, `info`, and simple project generation.

```tape
Output docs/vhs/basic-usage.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Explore available structures" Enter
Type "structkit list" Enter
Sleep 3
Type "" Enter
Type "# Get information about a specific structure" Enter
Type "structkit info terraform/module" Enter
Sleep 5
Type "" Enter
Type "# Generate a simple project structure" Enter
Type "structkit generate terraform/module ./my-terraform-module" Enter
Sleep 8
Type "" Enter
Type "# Verify the generated structure" Enter
Type "tree my-terraform-module" Enter
Sleep 5
```

### 3. YAML Configuration

**File**: `yaml-config.tape`
**Description**: Shows how to create and use custom YAML configuration files.

```tape
Output docs/vhs/yaml-config.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create a custom YAML configuration" Enter
Type "cat > my-project.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - README.md:" Enter
Type "      content: |" Enter
Type "        # {{@ project_name @}}" Enter
Type "        Welcome to my awesome project!" Enter
Type "  - src/main.py:" Enter
Type "      content: |" Enter
Type "        print('Hello from {{@ project_name @}}!')" Enter
Type "" Enter
Type "variables:" Enter
Type "  - project_name:" Enter
Type "      description: 'Name of your project'" Enter
Type "      type: string" Enter
Type "      default: 'MyProject'" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Generate structure from YAML (note: file:// is automatic)" Enter
Type "structkit generate my-project.yaml ./output" Enter
Sleep 5
Type "" Enter
Type "# Check the generated files" Enter
Type "tree output && echo && cat output/README.md" Enter
Sleep 5
```

### 4. Mappings & Variables

**File**: `mappings-demo.tape`
**Description**: Demonstrates external mappings files and template variables.

```tape
Output docs/vhs/mappings-demo.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create mappings file for environment variables" Enter
Type "cat > mappings.yaml << 'EOF'" Enter
Type "mappings:" Enter
Type "  environments:" Enter
Type "    dev:" Enter
Type "      database_url: 'postgres://localhost:5432/myapp_dev'" Enter
Type "      debug: true" Enter
Type "    prod:" Enter
Type "      database_url: 'postgres://prod-server:5432/myapp'" Enter
Type "      debug: false" Enter
Type "  teams:" Enter
Type "    devops: 'devops-team@company.com'" Enter
Type "    frontend: 'frontend-team@company.com'" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Create structure that uses mappings" Enter
Type "cat > app-config.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - config/{{@ env @}}.json:" Enter
Type "      content: |" Enter
Type "        {" Enter
Type "          \"database_url\": \"{{@ mappings.environments[env].database_url @}}\"," Enter
Type "          \"debug\": {{@ mappings.environments[env].debug @}}," Enter
Type "          \"contact\": \"{{@ mappings.teams.devops @}}\"" Enter
Type "        }" Enter
Type "variables:" Enter
Type "  - env:" Enter
Type "      description: 'Environment (dev/prod)'" Enter
Type "      type: string" Enter
Type "      default: 'dev'" Enter
Type "EOF" Enter
Sleep 3
Type "" Enter
Type "# Generate with mappings file" Enter
Type "structkit generate --mappings-file mappings.yaml app-config.yaml ./config-output" Enter
Sleep 5
Type "" Enter
Type "# Check generated configuration" Enter
Type "cat config-output/config/dev.json" Enter
Sleep 3
```

### 5. Multiple Mappings Files

**File**: `multiple-mappings.tape`
**Description**: Shows the new multiple mappings file feature with deep merging.

```tape
Output docs/vhs/multiple-mappings.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create base mappings file" Enter
Type "cat > base-mappings.yaml << 'EOF'" Enter
Type "mappings:" Enter
Type "  common:" Enter
Type "    app_name: 'MyApp'" Enter
Type "    version: '1.0.0'" Enter
Type "  environments:" Enter
Type "    dev:" Enter
Type "      replicas: 1" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Create environment-specific overrides" Enter
Type "cat > prod-mappings.yaml << 'EOF'" Enter
Type "mappings:" Enter
Type "  environments:" Enter
Type "    dev:" Enter
Type "      debug: true" Enter
Type "    prod:" Enter
Type "      replicas: 3" Enter
Type "      debug: false" Enter
Type "EOF" Enter
Sleep 2
Type "" Enter
Type "# Create deployment template" Enter
Type "cat > deployment.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - k8s/deployment.yaml:" Enter
Type "      content: |" Enter
Type "        apiVersion: apps/v1" Enter
Type "        kind: Deployment" Enter
Type "        metadata:" Enter
Type "          name: {{@ mappings.common.app_name @}}" Enter
Type "        spec:" Enter
Type "          replicas: {{@ mappings.environments[env].replicas @}}" Enter
Type "variables:" Enter
Type "  - env:" Enter
Type "      description: 'Target environment'" Enter
Type "      default: 'dev'" Enter
Type "EOF" Enter
Sleep 3
Type "" Enter
Type "# Generate with multiple mappings files (deep merge)" Enter
Type "structkit generate \\" Enter
Type "  --mappings-file base-mappings.yaml \\" Enter
Type "  --mappings-file prod-mappings.yaml \\" Enter
Type "  deployment.yaml ./k8s-output" Enter
Sleep 5
Type "" Enter
Type "# Check the merged result" Enter
Type "cat k8s-output/k8s/deployment.yaml" Enter
Sleep 3
```

### 6. Advanced Features

**File**: `advanced-features.tape`
**Description**: Demonstrates dry-run, file strategies, and validation.

```tape
Output docs/vhs/advanced-features.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create a test structure" Enter
Type "mkdir -p existing-project && echo 'old content' > existing-project/README.md" Enter
Sleep 1
Type "" Enter
Type "# Use dry-run to preview changes" Enter
Type "structkit generate --dry-run terraform/module ./existing-project" Enter
Sleep 5
Type "" Enter
Type "# Validate a YAML configuration" Enter
Type "cat > test-config.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - test.txt:" Enter
Type "      content: 'Hello World'" Enter
Type "EOF" Enter
Sleep 2
Type "structkit validate test-config.yaml" Enter
Sleep 3
Type "" Enter
Type "# Generate with backup strategy" Enter
Type "structkit generate --file-strategy=backup --backup=./backups terraform/module ./existing-project" Enter
Sleep 5
Type "" Enter
Type "# Check backup was created" Enter
Type "ls -la backups/ && echo && echo 'New content:' && head existing-project/README.md" Enter
Sleep 3
```

### 7. Remote Content & Protocols

**File**: `remote-content.tape`
**Description**: Shows fetching content from remote sources (GitHub, HTTP, etc.).

```tape
Output docs/vhs/remote-content.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Create structure using remote content" Enter
Type "cat > remote-demo.yaml << 'EOF'" Enter
Type "files:" Enter
Type "  - .gitignore:" Enter
Type "      file: github://github/gitignore/main/Python.gitignore" Enter
Type "  - LICENSE:" Enter
Type "      file: https://raw.githubusercontent.com/licenses/license-templates/master/templates/mit.txt" Enter
Type "  - README.md:" Enter
Type "      content: |" Enter
Type "        # {{@ project_name @}}" Enter
Type "        " Enter
Type "        This project uses remote content from GitHub." Enter
Type "variables:" Enter
Type "  - project_name:" Enter
Type "      description: 'Project name'" Enter
Type "      default: 'RemoteDemo'" Enter
Type "EOF" Enter
Sleep 3
Type "" Enter
Type "# Generate project with remote content" Enter
Type "structkit generate remote-demo.yaml ./remote-project" Enter
Sleep 8
Type "" Enter
Type "# Check downloaded content" Enter
Type "echo 'Generated files:' && ls -la remote-project/" Enter
Type "echo && echo 'First few lines of .gitignore:' && head -10 remote-project/.gitignore" Enter
Sleep 5
```

### 8. Schema Generation

**File**: `schema-generation.tape`
**Description**: Demonstrates the generate-schema command for IDE integration.

```tape
Output docs/vhs/schema-generation.gif

Set Theme "Monokai Vivid"
Set FontSize 14
Set TypingSpeed 40ms
Set WindowBar Colorful
Set BorderRadius 8
Set Margin 0
Set Padding 10
Set Width 1400
Set Height 800
Set Shell "bash"

Type "# Generate JSON schema for available structures" Enter
Type "structkit generate-schema" Enter
Sleep 5
Type "" Enter
Type "# Save schema to file for IDE integration" Enter
Type "structkit generate-schema -o struct-schema.json" Enter
Sleep 3
Type "" Enter
Type "# Check the generated schema" Enter
Type "echo 'Schema file created:' && ls -la struct-schema.json" Enter
Type "echo && echo 'Available structures in schema:' && jq -r '.definitions.PluginList.enum[]' struct-schema.json | head -10" Enter
Sleep 5
Type "" Enter
Type "# Schema can be used in VS Code for autocompletion" Enter
Type "echo 'Add to your .struct.yaml files for IDE support:'" Enter
Type "echo '# yaml-language-server: \$schema=./struct-schema.json'" Enter
Sleep 3
```

## 🎥 Creating the GIFs

To generate all the GIF animations, run:

```bash
# Install VHS if not already installed
go install github.com/charmbracelet/vhs@latest

# Generate all tapes
cd docs/vhs
vhs install.tape
vhs basic-usage.tape
vhs yaml-config.tape
vhs mappings-demo.tape
vhs multiple-mappings.tape
vhs advanced-features.tape
vhs remote-content.tape
vhs schema-generation.tape
```

## 📖 Usage in Documentation

These GIFs can be embedded in:

- **README.md** - Show installation and basic usage
- **docs/quickstart.md** - Include basic-usage.gif
- **docs/mappings.md** - Include mappings-demo.gif and multiple-mappings.gif
- **docs/configuration.md** - Include yaml-config.gif
- **docs/file-handling.md** - Include advanced-features.gif
- **docs/schema.md** - Include schema-generation.gif

Example markdown embedding:

```markdown
![StructKit Basic Usage](./docs/vhs/basic-usage.gif)
```

## ⚙️ VHS Configuration

All tapes use consistent settings:

- **Theme**: Monokai Vivid
- **Font Size**: 14
- **Typing Speed**: 40ms
- **Dimensions**: 1400x800
- **Shell**: bash

## 🔄 Updating Tapes

When StructKit features change:

1. Update the relevant tape file
2. Regenerate the GIF: `vhs filename.tape`
3. Commit both the tape and GIF files
4. Update documentation references if needed

---

These demonstrations provide comprehensive coverage of StructKit's capabilities, from basic usage to advanced features like multiple mappings files, remote content fetching, and schema generation.
