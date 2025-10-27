# Pre-generation and Post-generation Hooks

You can define shell commands to run before and after structure generation using the `pre_hooks` and `post_hooks` keys in your YAML configuration. These are optional and allow you to automate setup or cleanup steps.

## Hook Types

- **pre_hooks**: List of shell commands to run before generation. If any command fails (non-zero exit), generation is aborted.
- **post_hooks**: List of shell commands to run after generation completes. If any command fails, an error is shown.

## Basic Example

```yaml
pre_hooks:
  - echo "Preparing environment..."
  - ./scripts/prep.sh

post_hooks:
  - echo "Generation complete!"
  - ./scripts/cleanup.sh

files:
  - README.md:
      content: |
        # My Project
```

## How Hooks Work

### Pre-hooks

1. Execute in the order defined
2. Run before any files or folders are created
3. If any command returns non-zero exit code, generation stops
4. Useful for environment preparation, validation, or dependency checks

### Post-hooks

1. Execute after all files and folders are created
2. Run even if some file operations fail
3. Errors are reported but don't stop execution
4. Useful for cleanup, initialization, or notification tasks

## Output Handling

- Output from hooks (stdout and stderr) is shown in the terminal
- Hook execution is logged with appropriate log levels
- Failed hooks display error messages with exit codes

## Practical Examples

### Environment Setup

```yaml
pre_hooks:
  - python -m venv .venv
  - source .venv/bin/activate
  - pip install --upgrade pip

post_hooks:
  - source .venv/bin/activate
  - pip install -r requirements.txt
  - echo "Virtual environment ready!"

files:
  - requirements.txt:
      content: |
        flask==2.3.0
        requests==2.31.0
```

### Git Repository Initialization

```yaml
pre_hooks:
  - git --version  # Verify git is available

post_hooks:
  - git init
  - git add .
  - git commit -m "Initial commit from StructKit"
  - echo "Git repository initialized"

files:
  - .gitignore:
      file: github://github/gitignore/main/Python.gitignore
  - README.md:
      content: |
        # {{@ project_name @}}
        Generated with StructKit
```

### Docker Setup

```yaml
pre_hooks:
  - docker --version
  - echo "Setting up Docker environment..."

post_hooks:
  - docker build -t {{@ project_name | slugify @}} .
  - echo "Docker image built successfully"

files:
  - Dockerfile:
      content: |
        FROM python:3.11-slim
        WORKDIR /app
        COPY . .
        RUN pip install -r requirements.txt
        CMD ["python", "app.py"]
  - docker-compose.yml:
      content: |
        version: '3.8'
        services:
          app:
            build: .
            ports:
              - "8000:8000"
```

### Database Migration

```yaml
pre_hooks:
  - echo "Checking database connection..."
  - pg_isready -h localhost -p 5432

post_hooks:
  - python manage.py migrate
  - python manage.py collectstatic --noinput
  - echo "Database migrations complete"

files:
  - manage.py:
      content: |
        #!/usr/bin/env python
        import os
        import sys

        if __name__ == "__main__":
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)
```

### Testing and Validation

```yaml
pre_hooks:
  - echo "Validating prerequisites..."
  - node --version
  - npm --version

post_hooks:
  - npm install
  - npm run lint
  - npm test
  - echo "All tests passed!"

files:
  - package.json:
      content: |
        {
          "name": "{{@ project_name | slugify @}}",
          "version": "1.0.0",
          "scripts": {
            "test": "jest",
            "lint": "eslint src/"
          }
        }
```

## Best Practices

1. **Keep hooks simple**: Use external scripts for complex operations
2. **Handle errors gracefully**: Check for tool availability in pre-hooks
3. **Use absolute paths**: Hooks run in the target directory context
4. **Log important actions**: Use echo statements for user feedback
5. **Test independently**: Ensure hook commands work outside StructKit
6. **Consider dependencies**: Order hooks based on their requirements

## Error Handling

### Pre-hook Failures

```yaml
pre_hooks:
  - echo "Checking Python version..."
  - python --version || (echo "Python not found!" && exit 1)
  - echo "Python check passed"
```

### Post-hook Error Tolerance

```yaml
post_hooks:
  - npm install || echo "Warning: npm install failed"
  - git add . || echo "Warning: git add failed"
  - echo "Setup complete (some warnings may have occurred)"
```

## Variables in Hooks

You can use template variables in hook commands:

```yaml
pre_hooks:
  - echo "Setting up {{@ project_name @}}"
  - mkdir -p "{{@ project_name | slugify @}}"

post_hooks:
  - echo "{{@ project_name @}} setup complete!"
  - echo "Project created in: $(pwd)"

variables:
  - project_name:
      description: "Name of the project"
      type: string
      default: "MyProject"
```
