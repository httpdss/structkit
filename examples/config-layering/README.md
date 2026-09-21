# Config Layering Example

This example demonstrates how to use structkit's config layering system to set defaults at multiple levels.

## Overview

Structkit supports configuration at four levels (from lowest to highest priority):

1. **Built-in defaults** - Hard-coded baseline values
2. **User config** - Global defaults from `~/.config/struct/config.yaml`
3. **Project config** - Project-specific config from `.structkit.yaml` (legacy `.struct.yaml`) or `--config-file`
4. **CLI arguments** - Command-line flags (highest priority)

## Setup

### 1. Create a User Config

Set your personal global defaults:

```bash
mkdir -p ~/.config/struct
cat > ~/.config/struct/config.yaml << 'EOF'
# Personal defaults that apply to all projects
file_strategy: backup
input_store: ~/.cache/structkit/input.json
log: WARNING
EOF
```

### 2. Create a Project Config

Create a project-specific config file:

```bash
cat > project-config.yaml << 'EOF'
# Project-specific overrides
file_strategy: skip
structures_path: ./custom-structures
backup: ./backups
EOF
```

## Usage

### View Effective Configuration

Display the merged configuration after all layers are applied:

```bash
# View with user config only
structkit config print

# View with project config override
structkit config print -c project-config.yaml

# View in JSON format
structkit config print --format json

# Override with CLI args
structkit config print -c project-config.yaml --log DEBUG
```

### Example Output

With user config only:
```yaml
file_strategy: backup
input_store: /home/user/.cache/structkit/input.json
log: WARNING
non_interactive: false
output: file

Configuration sources:
  1. Built-in defaults: always loaded
  2. User config: /home/user/.config/struct/config.yaml (exists)
  3. Project config: none specified
  4. CLI arguments: highest priority
```

With project config override:
```yaml
backup: ./backups
file_strategy: skip
input_store: /home/user/.cache/structkit/input.json
log: WARNING
non_interactive: false
output: file
structures_path: ./custom-structures

Configuration sources:
  1. Built-in defaults: always loaded
  2. User config: /home/user/.config/struct/config.yaml (exists)
  3. Project config: project-config.yaml
  4. CLI arguments: highest priority
```

Notice how:
- `file_strategy` changed from `backup` (user config) to `skip` (project config)
- `input_store` remained from user config (not overridden by project)
- `structures_path` and `backup` are new from project config

## Supported Config Options

The following options can be set in config files:

- `structures_path` - Path to custom structure definitions
- `source` - Named source for structure definitions
- `input_store` - Path to the input store file
- `file_strategy` - Strategy for handling existing files (`overwrite`, `skip`, `append`, `rename`, `backup`)
- `backup` - Path to backup folder
- `global_system_prompt` - Global system prompt for OpenAI
- `non_interactive` - Run in non-interactive mode (boolean)
- `output` - Output mode (`file` or `console`)
- `log` - Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `log_file` - Path to log file

## Precedence Rules

When the same option is set at multiple levels:

1. CLI arguments always win
2. Project config overrides user config
3. User config overrides built-in defaults
4. Built-in defaults are always present

## Common Use Cases

### Personal Backup Strategy

Set your preferred file strategy globally:
```yaml
# ~/.config/struct/config.yaml
file_strategy: backup
backup: ~/structkit-backups
```

### Team Project Standards

Share project-specific settings in version control:
```yaml
# .structkit.yaml (checked into git)
structures_path: ./team-structures
input_store: ./.structkit/input.json
non_interactive: true
```

### Temporary Overrides

Override for a single command:
```bash
structkit generate --file-strategy overwrite --log DEBUG
```

## Tips

1. Use user config for personal preferences that apply to all projects
2. Use project config for team standards and project-specific paths
3. Use CLI args for one-off overrides during development
4. Run `structkit config print` to debug configuration issues
