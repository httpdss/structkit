# Environment Variables

StructKit supports environment variables to configure CLI arguments without requiring them to be specified on the command line. This is particularly useful for CI/CD pipelines, containerized environments, and automation workflows.

## Overview

Environment variables allow you to set default values for CLI arguments. Command-line arguments always take precedence over environment variables, ensuring flexibility when needed.

## High Priority Environment Variables

### `STRUCTKIT_GLOBAL_SYSTEM_PROMPT`

Sets the global system prompt for OpenAI integration.

**CLI Equivalent:** `--global-system-prompt` / `-p`

**Use Case:** Typically a long or sensitive value that users want to set once. Avoids repeating the same prompt across multiple invocations. Ideal for CI/CD workflows and container initialization.

**Example:**
```bash
export STRUCTKIT_GLOBAL_SYSTEM_PROMPT="You are a helpful assistant for generating project structures."
structkit generate my-structure ./output
```

### `STRUCTKIT_INPUT_STORE`

Sets the path to the input store for template variables.

**CLI Equivalent:** `--input-store` / `-n`

**Default:** `/tmp/structkit/input.json`

**Use Case:** Allows users to set a consistent default location for input data. Useful for workflows that need persistent input across multiple runs.

**Example:**
```bash
export STRUCTKIT_INPUT_STORE="/home/user/structkit-inputs/data.json"
structkit generate my-structure ./output
```

### `STRUCTKIT_BACKUP_PATH`

Sets the default backup location for file backups.

**CLI Equivalent:** `--backup` / `-b`

**Use Case:** Set a default backup location project-wide or environment-wide. Saves typing in repetitive operations. Useful for ensuring backups go to a specific location (e.g., mounted volume in containers).

**Example:**
```bash
export STRUCTKIT_BACKUP_PATH="/backups/structkit"
structkit generate my-structure ./output
```

## Medium Priority Environment Variables

### `STRUCTKIT_FILE_STRATEGY`

Sets the default strategy for handling existing files.

**CLI Equivalent:** `--file-strategy` / `-f`

**Valid Values:** `overwrite`, `skip`, `append`, `rename`, `backup`

**Default:** `overwrite`

**Use Case:** Let users set a preferred default strategy. Could prevent accidental data loss if set to 'skip' or 'backup' by default.

**Example:**
```bash
export STRUCTKIT_FILE_STRATEGY="backup"
structkit generate my-structure ./output
```

### `STRUCTKIT_NON_INTERACTIVE`

Enables or disables interactive mode for all commands.

**CLI Equivalent:** `--non-interactive`

**Valid Values:** `true`, `1`, `yes` (case-insensitive) for enabled; any other value for disabled

**Default:** `false`

**Use Case:** Boolean flag useful for CI/CD pipelines. Could be set in environment and applied across all commands.

**Example:**
```bash
export STRUCTKIT_NON_INTERACTIVE=true
structkit generate my-structure ./output
```

### `STRUCTKIT_OUTPUT_MODE`

Sets the default output mode for the generate command.

**CLI Equivalent:** `--output` / `-o`

**Valid Values:** `console`, `file`

**Default:** `file`

**Use Case:** Some users might prefer 'console' output by default. Useful for pipeline integration.

**Example:**
```bash
export STRUCTKIT_OUTPUT_MODE="console"
structkit generate my-structure ./output
```

## Shared Environment Variables

### `STRUCTKIT_STRUCTURES_PATH`

Sets the path to custom structure definitions.

**CLI Equivalent:** `--structures-path` / `-s`

**Use Case:** Allows specifying custom structures directory that applies across all commands (generate, list, info, generate-schema).

**Example:**
```bash
export STRUCTKIT_STRUCTURES_PATH="/home/user/my-structures"
structkit list
structkit generate my-custom-structure ./output
```

### `STRUCTKIT_LOG_LEVEL`

Sets the logging level for all commands.

**CLI Equivalent:** `--log` (generate command)

**Valid Values:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

**Default:** `INFO`

**Use Case:** Control verbosity of output for debugging or production deployments.

**Example:**
```bash
export STRUCTKIT_LOG_LEVEL="DEBUG"
structkit generate my-structure ./output
```

## Precedence Rules

Command-line arguments **always take precedence** over environment variables. This allows environment variables to set sensible defaults while maintaining the ability to override them when needed.

**Precedence Order (highest to lowest):**
1. Command-line arguments
2. Environment variables
3. Built-in defaults

**Example:**
```bash
# Set default via environment variable
export STRUCTKIT_FILE_STRATEGY="backup"

# Override with CLI argument
structkit generate --file-strategy skip my-structure ./output
# Uses 'skip', not 'backup'

# Use default from environment
structkit generate my-structure ./output
# Uses 'backup' from STRUCTKIT_FILE_STRATEGY
```

## Docker and Containerization

Environment variables are particularly useful when running StructKit in containers:

**Docker Example:**
```bash
docker run \
  -e STRUCTKIT_STRUCTURES_PATH=/custom/structures \
  -e STRUCTKIT_NON_INTERACTIVE=true \
  -e STRUCTKIT_FILE_STRATEGY=backup \
  -v /custom/structures:/custom/structures \
  -v $(pwd):/workdir \
  ghcr.io/httpdss/structkit:main generate my-structure /workdir/output
```

**Docker Compose Example:**
```yaml
version: '3'
services:
  structkit:
    image: ghcr.io/httpdss/structkit:main
    environment:
      STRUCTKIT_STRUCTURES_PATH: /custom/structures
      STRUCTKIT_NON_INTERACTIVE: "true"
      STRUCTKIT_FILE_STRATEGY: backup
      STRUCTKIT_LOG_LEVEL: DEBUG
    volumes:
      - /custom/structures:/custom/structures
      - ./output:/workdir
    command: generate my-structure /workdir/output
```

## CI/CD Pipeline Integration

### GitHub Actions - Basic Example

```yaml
name: Generate Project Structure

on: [push, pull_request]

jobs:
  generate:
    runs-on: ubuntu-latest
    env:
      STRUCTKIT_NON_INTERACTIVE: "true"
      STRUCTKIT_BACKUP_PATH: /tmp/backups
      STRUCTKIT_FILE_STRATEGY: backup
    steps:
      - uses: actions/checkout@v3

      - name: Install StructKit
        run: pip install structkit

      - name: Generate structure
        run: structkit generate my-structure ./generated-project

      - name: Upload generated files
        uses: actions/upload-artifact@v3
        with:
          name: generated-project
          path: generated-project/
```

### GitHub Actions - Advanced Example with Custom Structures

```yaml
name: Generate with Custom Structures

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    env:
      STRUCTKIT_NON_INTERACTIVE: "true"
      STRUCTKIT_LOG_LEVEL: DEBUG
      STRUCTKIT_OUTPUT_MODE: console
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install StructKit
        run: pip install structkit

      - name: Generate default structure
        run: structkit generate python-basic ./my-project

      - name: Generate with custom backup strategy
        env:
          STRUCTKIT_BACKUP_PATH: ./backups
          STRUCTKIT_FILE_STRATEGY: backup
        run: structkit generate terraform-module ./my-infrastructure

      - name: Create summary
        run: |
          echo "## Generated Structures" >> $GITHUB_STEP_SUMMARY
          echo "- Python project generated" >> $GITHUB_STEP_SUMMARY
          echo "- Terraform module generated" >> $GITHUB_STEP_SUMMARY
```

## Best Practices

1. **Use Environment Variables for Defaults** - Set environment variables for values that don't change frequently
2. **Override When Needed** - Use CLI arguments for one-off changes or specific use cases
3. **Document Configuration** - Document which environment variables are used in your project
4. **Sensitive Data** - Store sensitive data (like API keys) in environment variables, not in configuration files
5. **Validation** - Test environment variable configuration to ensure it works as expected

## Troubleshooting

### Environment variable not being picked up

1. Verify the environment variable is set: `echo $VARIABLE_NAME`
2. Ensure you're using the correct variable name (case-sensitive on Linux/macOS)
3. If running in Docker, check that the environment variable is passed correctly with `-e`
4. Restart your terminal or shell session after setting the variable

### CLI argument not overriding environment variable

This should not happen - CLI arguments always take precedence. If you're experiencing this:
1. Verify the CLI argument is correctly formatted
2. Check that you're using the correct argument name (e.g., `--file-strategy` not `--strategy`)
3. Ensure there are no spaces or special characters in the argument value

### Boolean environment variables not working correctly

For `STRUCTKIT_NON_INTERACTIVE`, only `true`, `1`, and `yes` (case-insensitive, e.g., `"True"`, `"TRUE"`, `"YeS"`) are recognized as true values. All other values are treated as false, including:
- `"true "` (with trailing space)
- `"on"` or `"enable"`

Use one of the recognized values for reliable behavior.
