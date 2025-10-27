# YAML Schema Reference

StructKit provides JSON schema validation to ensure your YAML configuration files are correctly structured. This helps catch errors early and provides IDE support with autocompletion.

## Schema Location

The official schema is available at:

```text
https://raw.githubusercontent.com/httpdss/structkit/main/struct-schema.json
```

## IDE Configuration

### VS Code

1. Install the [YAML extension](https://marketplace.visualstudio.com/items?itemName=redhat.vscode-yaml)
2. Add this to your workspace settings (`.vscode/settings.json`):

```json
{
  "yaml.schemas": {
    "https://raw.githubusercontent.com/httpdss/structkit/main/struct-schema.json": ".struct.yaml"
  }
}
```

This provides validation and autocompletion for all `.struct.yaml` files.

### JetBrains IDEs (IntelliJ, PyCharm, etc.)

1. Go to **Settings** → **Languages & Frameworks** → **Schemas and DTDs** → **JSON Schema Mappings**
2. Click **+** to add a new mapping
3. Set **Schema file or URL** to: `https://raw.githubusercontent.com/httpdss/structkit/main/struct-schema.json`
4. Set **File path pattern** to: `*.struct.yaml`

## Generating Custom Schema

If you have custom structures, generate a schema that includes them:

```sh
# Generate schema with custom structures
structkit generate-schema -s /path/to/custom/structures -o my-schema.json

# Use in VS Code settings
{
  "yaml.schemas": {
    "./my-schema.json": ".struct.yaml"
  }
}
```

## Schema Structure

The schema validates the following top-level properties:

### `files` (array)

Defines files to be created:

```yaml
files:
  - filename.txt:
      content: "File contents"
      permissions: "0644"
      skip: false
      skip_if_exists: false
      file: "https://example.com/template.txt"
```

**Properties:**

- `content` (string): Inline file content
- `permissions` (string): Octal permissions (e.g., "0755")
- `skip` (boolean): Skip file creation
- `skip_if_exists` (boolean): Skip if file exists
- `file` (string): External file URL or path

### `folders` (array)

Defines folders and nested structures:

```yaml
folders:
  - path/to/folder:
      struct: "structure-name"
      with:
        variable: "value"
```

**Properties:**

- `struct` (string|array): Structure name(s) to apply
- `with` (object): Variables to pass to the structure

### `variables` (array)

Defines template variables:

```yaml
variables:
  - variable_name:
      description: "Variable description"
      type: "string"
      default: "default_value"
```

**Properties:**

- `description` (string): Human-readable description
- `type` (string): Variable type (string, integer, boolean)
- `default` (any): Default value

### `pre_hooks` (array)

Shell commands to run before generation:

```yaml
pre_hooks:
  - "echo 'Starting generation...'"
  - "./scripts/prepare.sh"
```

### `post_hooks` (array)

Shell commands to run after generation:

```yaml
post_hooks:
  - "npm install"
  - "git init"
```

## Validation

### Command Line Validation

```sh
# Validate a configuration file
structkit validate my-config.yaml
```

### Programmatic Validation

```python
import json
import yaml
from jsonschema import validate

# Load schema
with open('struct-schema.json') as f:
    schema = json.load(f)

# Load and validate config
with open('my-config.yaml') as f:
    config = yaml.safe_load(f)

validate(config, schema)  # Raises exception if invalid
```

## Common Validation Errors

### Invalid File Structure

```yaml
# ❌ Wrong - files should be array of objects
files:
  README.md: "content"

# ✅ Correct
files:
  - README.md:
      content: "content"
```

### Missing Required Properties

```yaml
# ❌ Wrong - structkit property missing
folders:
  - src/:
      with:
        name: "myapp"

# ✅ Correct
folders:
  - src/:
      struct: "project/node"
      with:
        name: "myapp"
```

### Invalid Variable Types

```yaml
# ❌ Wrong - type should be string
variables:
  - port:
      type: number
      default: 8080

# ✅ Correct
variables:
  - port:
      type: integer
      default: 8080
```

## Schema Extensions

You can extend the base schema for custom validation:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "allOf": [
    {
      "$ref": "https://raw.githubusercontent.com/httpdss/structkit/main/struct-schema.json"
    },
    {
      "properties": {
        "custom_section": {
          "type": "object",
          "properties": {
            "custom_property": {"type": "string"}
          }
        }
      }
    }
  ]
}
```

## IDE Benefits

With schema validation enabled, you get:

- **Real-time validation**: Errors highlighted as you type
- **Autocompletion**: Suggested properties and values
- **Documentation**: Hover tooltips with property descriptions
- **Structure guidance**: Valid structure names and paths

## Troubleshooting

### Schema Not Loading

1. Check internet connection (for remote schema)
2. Verify file path (for local schema)
3. Restart IDE after configuration changes
4. Check IDE logs for error messages

### Validation Errors

1. Use `structkit validate` command for detailed error messages
2. Check schema documentation for required properties
3. Verify YAML syntax is correct
4. Ensure structure names exist in your installation

### Performance Issues

1. Use local schema files for better performance
2. Consider schema caching in your IDE
3. Limit schema complexity for large configurations

This schema system ensures your StructKit configurations are valid and provides a better development experience through IDE integration.
