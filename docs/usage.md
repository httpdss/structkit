# Basic Usage

Run the script with the following command using one of the following subcommands:

- `generate`: Generate the project structure based on the YAML configuration.
- `generate-schema`: Generate JSON schema for available structure templates.
- `validate`: Validate the YAML configuration file.
- `info`: Display information about the script and its dependencies.
- `list`: List the available structs

For more information, run the script with the `-h` or `--help` option (this is also available for each subcommand):

![StructKit List](./vhs/basic-usage.gif)

```sh
structkit -h
```

## Generate Command

### Finding Available Structures

Use the `list` command to see all available structures:

```sh
structkit list
```

Or if you have [auto-completion](completion.md) enabled, use `Tab` to see all options:

```sh
structkit generate <Tab>
# Shows all available structures
```

### Using Defaults

If you have a .struct.yaml in the current directory and want to generate into the current directory, you can simply run:

```sh
structkit generate
```

### Simple Example

```sh
structkit generate terraform/modules/generic ./my-terraform-module
```

### YAML File Usage

For local YAML configuration files, the `file://` protocol is automatically added:

```sh
# Both of these work identically
structkit generate my-config.yaml ./output
structkit generate file://my-config.yaml ./output
```

Tip: If your config file is named `.struct.yaml` in the current directory and you want to generate into the current directory, you can simply run:

```sh
structkit generate
```

### Diff Preview Example

```sh
structkit generate --dry-run --diff file://structure.yaml ./output
```

### Complete Example

```sh
structkit generate \
  --log=DEBUG \
  --dry-run \
  --backup=/path/to/backup \
  --file-strategy=rename \
  --log-file=/path/to/logfile.log \
  terraform-module \
  ./my-terraform-module
```

### Command Options

- `--log`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `--dry-run`: Preview actions without making changes
- `--diff`: Show unified diffs for files that would be created/modified (useful with `--dry-run` and console output)
- `--backup`: Specify backup directory for existing files
- `--file-strategy`: Choose how to handle existing files (overwrite, skip, append, rename, backup)
- `--log-file`: Write logs to specified file
- `--mappings-file`: Provide external mappings file (can be used multiple times)

## Generate Schema Command

The `generate-schema` command creates JSON schema definitions for available structure templates, making it easier for tools and IDEs to provide autocompletion and validation.

### Basic Usage of `generate-schema`

```sh
# Generate schema to stdout
structkit generate-schema

# Generate schema with custom structures path
structkit generate-schema -s /path/to/custom/structures

# Save schema to file
structkit generate-schema -o schema.json

# Combine custom path and output file
structkit generate-schema -s /path/to/custom/structures -o schema.json
```

### Command Options for `generate-schema`

- `-s, --structures-path`: Path to additional structure definitions (optional)
- `-o, --output`: Output file path for the schema (default: stdout)

The generated schema includes all available structures from both the built-in contribs directory and any custom structures path you specify. This is useful for:

- IDE autocompletion when writing `.struct.yaml` files
- Validation of structure references in your configurations
- Programmatic discovery of available templates

## Other Commands

### Initialize a project with .struct.yaml

Create a minimal .struct.yaml in the current directory:

```sh
structkit init
```

Or specify a directory:

```sh
structkit init ./my-project
```

The file includes:

- pre_hooks/post_hooks with echo commands
- A README.md placeholder in files
- A folders entry pointing to the github/workflows/run-structkit workflow at ./

### Validate Configuration

```sh
structkit validate my-structure.yaml
```

### List Available Structures

```sh
structkit list
```

### Show Information

```sh
structkit info <structure_definition>
```
