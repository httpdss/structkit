# File Handling

StructKit provides flexible options for handling files and managing permissions.

## File Properties

### Basic Properties

- **skip**: Skip file/folder creation entirely
- **skip_if_exists**: Skip only if the file already exists
- **permissions**: Set custom file permissions
- **content**: Define file content inline
- **file**: Reference external file content

### Skip Behavior

```yaml
files:
  - README.md:
      skip: true  # Never create this file
      content: "This won't be created"

  - config.yml:
      skip_if_exists: true  # Only create if it doesn't exist
      content: "default: value"
```

### File Permissions

Set custom permissions using octal notation:

```yaml
files:
  - scripts/deploy.sh:
      permissions: '0755'  # Executable script
      content: |
        #!/bin/bash
        echo "Deploying..."

  - secrets/api.key:
      permissions: '0600'  # Read-only for owner
      content: "{{@ api_key @}}"
```

## Content Sources

### Inline Content

Define content directly in the YAML:

```yaml
files:
  - app.py:
      content: |
        #!/usr/bin/env python3
        print("Hello, {{@ project_name @}}!")
```

### External Files

Reference local or remote files:

```yaml
files:
  - LICENSE:
      file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
```

## Remote File Protocols

StructKit supports multiple protocols for fetching remote content (with caching and robust fallbacks):

### HTTP/HTTPS

```yaml
files:
  - requirements.txt:
      file: https://raw.githubusercontent.com/example/repo/main/requirements.txt
```

### GitHub Protocols

StructKit optimizes single-file fetches from GitHub by preferring `raw.githubusercontent.com` when possible and falling back to `git clone/pull` if necessary. You can control behavior with environment variables:

- `STRUCTKIT_HTTP_TIMEOUT` (seconds, default 10)
- `STRUCTKIT_HTTP_RETRIES` (default 2)
- `STRUCTKIT_DENY_NETWORK=1` to skip HTTP attempts and use git fallback directly.

#### Standard GitHub

```yaml
files:
  - .gitignore:
      file: github://github/gitignore/main/Python.gitignore
```

#### GitHub HTTPS

```yaml
files:
  - workflow.yml:
      file: githubhttps://actions/starter-workflows/main/ci/python-app.yml
```

#### GitHub SSH

```yaml
files:
  - private-config.yml:
      file: githubssh://company/private-repo/main/config/template.yml
```

### Cloud Storage

#### Amazon S3

```yaml
files:
  - data.csv:
      file: s3://my-bucket/data/template.csv
```

#### Google Cloud Storage

```yaml
files:
  - config.json:
      file: gs://my-bucket/configs/default.json
```

## File Handling Strategies

Control how StructKit handles existing files with the `--file-strategy` option:

### Available Strategies

- **overwrite**: Replace existing files (default)
- **skip**: Skip files that already exist
- **append**: Add content to existing files
- **rename**: Rename existing files with a suffix
- **backup**: Move existing files to backup directory

### Usage Examples

```sh
# Skip existing files
structkit generate --file-strategy=skip my-config.yaml ./output

# Backup existing files
structkit generate --file-strategy=backup --backup=/tmp/backup my-config.yaml ./output

# Rename existing files
structkit generate --file-strategy=rename my-config.yaml ./output
```

> **Note**: The `file://` protocol is automatically added for `.yaml` files, so these examples work with or without the explicit protocol.

## Advanced Examples

### Conditional File Creation

```yaml
files:
  - docker-compose.yml:
      skip: "{{@ not use_docker @}}"
      content: |
        version: '3.8'
        services:
          app:
            build: .

  - Dockerfile:
      skip_if_exists: true
      permissions: '0644'
      file: https://raw.githubusercontent.com/example/dockerfiles/main/python.Dockerfile
```

### Dynamic Permissions

```yaml
files:
  - "scripts/{{@ script_name @}}.sh":
      permissions: '0755'
      content: |
        #!/bin/bash
        # {{@ script_description @}}
        echo "Running {{@ script_name @}}"
```

### Multiple Content Sources

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}

        ## Installation

        ```bash
        pip install -r requirements.txt
        ```

  - requirements.txt:
      file: https://raw.githubusercontent.com/example/templates/main/python-requirements.txt

  - .env.example:
      file: file://./templates/env-template
```

## Best Practices

1. **Use `skip_if_exists`** for configuration files that shouldn't be overwritten
2. **Set appropriate permissions** for scripts and sensitive files
3. **Use remote files** for standardized content like licenses and gitignores
4. **Combine strategies** with command-line options for different deployment scenarios
5. **Test with `--dry-run`** before applying changes to important directories
