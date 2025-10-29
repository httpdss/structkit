# CLI Reference

This document provides a reference for the `struct` command-line interface (CLI).

## Overview

The `struct` CLI allows you to generate project structures from YAML configuration files. It supports both built-in structure definitions and custom structures.

**Basic Usage:**

```sh
structkit {info,validate,generate,list,generate-schema,mcp,completion,init} ...
```

## Global Options

These options are available for all commands:

- `-h, --help`: Show the help message and exit.
- `-l LOG, --log LOG`: Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
- `-c CONFIG_FILE, --config-file CONFIG_FILE`: Path to a configuration file.
- `-i LOG_FILE, --log-file LOG_FILE`: Path to a log file.

## Environment Variables

The following environment variables can be used to configure default values for CLI arguments:

- `STRUCTKIT_LOG_LEVEL`: Set the default logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Overridden by the `--log` flag.
- `STRUCTKIT_STRUCTURES_PATH`: Set the default path to structure definitions. This is used as the default value for the `--structures-path` flag when not explicitly provided. When set, the CLI will log an info message indicating that this environment variable is being used.

**Precedence:**

1. Explicit `--structures-path` CLI flag (highest priority)
2. `STRUCTKIT_STRUCTURES_PATH` environment variable
3. Default system paths (lowest priority)

**Example:**

```sh
# Set a default structures path
export STRUCTKIT_STRUCTURES_PATH=~/custom-structures

# Now you can omit the -s flag
structkit generate python-basic ./my-project
# Equivalent to: structkit generate -s ~/custom-structures python-basic ./my-project

# CLI flag takes precedence over environment variable
structkit generate -s /another/path python-basic ./my-project
# This will use /another/path, not ~/custom-structures
```

## Commands

### `info`

Show information about a structure definition.

**Usage:**

```sh
structkit info [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH] structure_definition
```

**Arguments:**

- `structure_definition`: Name of the structure definition.
- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.

### `validate`

Validate the YAML configuration file.

**Usage:**

```sh
structkit validate [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] yaml_file
```

**Arguments:**

- `yaml_file`: Path to the YAML configuration file.

### `generate`

Generate the project structure.

**Usage:**

```sh
structkit generate [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH] [-n INPUT_STORE] [-d] [--diff] [-v VARS] [-b BACKUP] [-f {overwrite,skip,append,rename,backup}] [-p GLOBAL_SYSTEM_PROMPT] [--non-interactive] [--mappings-file MAPPINGS_FILE] [-o {console,file}] [structure_definition] [base_path]
```

Defaults when omitted:
- structure_definition -> .struct.yaml
- base_path -> .

Example:
```sh
structkit generate
```

**Arguments:**

- `structure_definition` (optional): Path to the YAML configuration file (default: `.struct.yaml`).
- `base_path` (optional): Base path where the structure will be created (default: `.`).
- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions. Can be set via the `STRUCTKIT_STRUCTURES_PATH` environment variable. When using the environment variable (and no explicit CLI flag), an info-level log message will be emitted indicating which path is being used.
- `-n INPUT_STORE, --input-store INPUT_STORE`: Path to the input store.
- `-d, --dry-run`: Perform a dry run without creating any files or directories.
- `--diff`: Show unified diffs for files that would be created/modified (works with `--dry-run` and in `-o console` mode).
- `-v VARS, --vars VARS`: Template variables in the format KEY1=value1,KEY2=value2.
- `-b BACKUP, --backup BACKUP`: Path to the backup folder.
- `-f {overwrite,skip,append,rename,backup}, --file-strategy {overwrite,skip,append,rename,backup}`: Strategy for handling existing files.
- `-p GLOBAL_SYSTEM_PROMPT, --global-system-prompt GLOBAL_SYSTEM_PROMPT`: Global system prompt for OpenAI.
- `--non-interactive`: Run the command in non-interactive mode.
- `--mappings-file MAPPINGS_FILE`: Path to a YAML file containing mappings to be used in templates (can be specified multiple times).
- `-o {console,file}, --output {console,file}`: Output mode.

### `list`

List available structures.

**Usage:**

```sh
structkit list [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH]
```

**Arguments:**

- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.

### `generate-schema`

Generate JSON schema for available structures.

**Usage:**

```sh
structkit generate-schema [-h] [-l LOG] [-c CONFIG_FILE] [-i LOG_FILE] [-s STRUCTURES_PATH] [-o OUTPUT]
```

**Arguments:**

- `-s STRUCTURES_PATH, --structures-path STRUCTURES_PATH`: Path to structure definitions.
- `-o OUTPUT, --output OUTPUT`: Output file path for the schema (default: stdout).

### `completion`

Manage shell completions for struct.

Usage:

```sh
structkit completion install [bash|zsh|fish]
```

- If no shell is provided, the command attempts to auto-detect your current shell and prints the exact commands to generate and install static completion files via shtab.
- This does not modify your shell configuration; it only prints the commands you can copy-paste.

### `init`

Initialize a basic .struct.yaml in the target directory.

Usage:

```sh
structkit init [path]
```

- Creates a .struct.yaml if it does not exist.
- Includes:
  - pre_hooks/post_hooks with echo commands
  - files with a README.md placeholder
  - folders referencing github/workflows/run-structkit at ./
- Non-destructive: if .struct.yaml already exists, it is not overwritten and a message is printed.

## Examples

### Using Defaults

Generate with default structure (.struct.yaml) into current directory:

```sh
structkit generate
```

### Basic Structure Generation

Generate a structure using a built-in definition:

```sh
structkit generate python-basic ./my-project
```

Generate from a custom YAML file:

```sh
structkit generate file://my-structure.yaml ./output-dir
```

### Using Custom Structures

Generate with custom structure path:

```sh
structkit generate -s ~/custom-structures python-api ./my-api
```

### Template Variables

Pass template variables to the structure:

```sh
structkit generate -v "project_name=MyApp,author=John Doe" file://structure.yaml ./output
```

### Dry Run

Test structure generation without creating files:

```sh
structkit generate -d file://structure.yaml ./output
```

### File Strategies

Handle existing files with different strategies:

```sh
# Skip existing files
structkit generate -f skip file://structure.yaml ./output

# Backup existing files
structkit generate -f backup -b ./backup file://structure.yaml ./output
```

### Console Output

Output to console instead of creating files:

```sh
structkit generate -o console file://structure.yaml ./output
```

### Validation

Validate a YAML configuration before generation:

```sh
structkit validate my-structure.yaml
```

### List Available Structures

List all built-in structures:

```sh
structkit list
```

List structures from custom path:

```sh
structkit list -s ~/custom-structures
```

### Get Structure Information

Get detailed information about a structure:

```sh
structkit info python-basic
```

### Generate Schema

Generate JSON schema and save to file:

```sh
structkit generate-schema -o schema.json
```
