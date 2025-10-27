# Examples

This page contains practical examples of StructKit configurations for various use cases.

## Basic Examples

### Simple Project

Basic project structure with files and folders:

```yaml
# Example: Simple Project Structure
# Use case: Basic project setup with common files

files:
  - README.md:
      content: |
        # {{@ project_name | default('My Project') @}}

        Welcome to the project!

        ## Getting Started

        1. Install dependencies
        2. Run the application
        3. Enjoy!

  - .gitignore:
      content: |
        node_modules/
        *.log
        .env
        dist/

  - LICENSE:
      content: |
        MIT License

        Copyright (c) {{@ year | default('2024') @}} {{@ author | default('Project Author') @}}

folders:
  - src/:
      struct:
        - basic/folder
  - docs/:
      struct:
        - basic/folder

variables:
  - project_name:
      description: 'Name of the project'
      type: string
      default: 'My Project'
  - author:
      description: 'Project author'
      type: string
      default: 'Project Author'
  - year:
      description: 'Copyright year'
      type: string
      default: '2024'
```

### Template Variables

Using dynamic content with variables:

```yaml
# Example: Template Variables
# Use case: Dynamic content generation with user input

files:
  - package.json:
      content: |
        {
          "name": "{{@ package_name @}}",
          "version": "{{@ version | default('1.0.0') @}}",
          "description": "{{@ description @}}",
          "author": "{{@ author @}}",
          "license": "{{@ license | default('MIT') @}}"
        }

  - src/config.js:
      content: |
        module.exports = {
          appName: '{{@ app_name @}}',
          version: '{{@ version | default('1.0.0') @}}',
          environment: '{{@ environment | default('development') @}}'
        };

variables:
  - package_name:
      description: 'NPM package name'
      type: string
      required: true
  - app_name:
      description: 'Application display name'
      type: string
      required: true
  - description:
      description: 'Project description'
      type: string
      required: true
  - author:
      description: 'Package author'
      type: string
      required: true
  - version:
      description: 'Initial version'
      type: string
      default: '1.0.0'
  - license:
      description: 'License type'
      type: string
      default: 'MIT'
  - environment:
      description: 'Target environment'
      type: string
      default: 'development'
```

### Remote Files

Fetching content from external sources:

```yaml
# Example: Remote Files
# Use case: Including content from external URLs or repositories

files:
  - .gitignore:
      remote: 'https://raw.githubusercontent.com/github/gitignore/main/Node.gitignore'

  - CODE_OF_CONDUCT.md:
      remote: 'https://raw.githubusercontent.com/contributor-covenant/contributor-covenant/main/CODE_OF_CONDUCT.md'

  - CONTRIBUTING.md:
      content: |
        # Contributing to {{@ project_name @}}

        Thank you for your interest in contributing!

        ## Development Setup

        1. Fork the repository
        2. Clone your fork
        3. Install dependencies
        4. Make your changes
        5. Submit a pull request

variables:
  - project_name:
      description: 'Project name'
      type: string
      required: true
```

## Application Development

### Python Project

Complete Python application structure:

````yaml
# Example: Python Project
# Use case: Full Python application with proper structure

files:
  - README.md:
      content: |
        # {{@ project_name @}}

        {{@ description @}}

        ## Installation

        ```bash
        pip install -r requirements.txt
        ```

        ## Usage

        ```bash
        python -m {{@ package_name @}}
        ```

  - requirements.txt:
      content: |
        click>=8.0.0
        requests>=2.25.0
        pytest>=6.0.0

  - setup.py:
      content: |
        from setuptools import setup, find_packages

        setup(
            name="{{@ package_name @}}",
            version="{{@ version | default('0.1.0') @}}",
            description="{{@ description @}}",
            author="{{@ author @}}",
            packages=find_packages(),
            install_requires=[
                "click>=8.0.0",
                "requests>=2.25.0",
            ],
            entry_points={
                "console_scripts": [
                    "{{@ package_name @}}={{@ package_name @}}.cli:main",
                ],
            },
        )

  - '{{@ package_name @}}/__init__.py':
      content: |
        """{{@ description @}}"""
        __version__ = "{{@ version | default('0.1.0') @}}"

  - '{{@ package_name @}}/main.py':
      content: |
        """Main application module."""

        def main():
            """Main entry point."""
            print("Hello from {{@ project_name @}}!")

        if __name__ == "__main__":
            main()

  - tests/test_main.py:
      content: |
        """Tests for main module."""
        import pytest
        from {{@ package_name @}} import main

        def test_main():
            """Test main function."""
            # Add your tests here
            assert True

variables:
  - project_name:
      description: 'Project name'
      type: string
      required: true
  - package_name:
      description: 'Python package name'
      type: string
      required: true
  - description:
      description: 'Project description'
      type: string
      required: true
  - author:
      description: 'Project author'
      type: string
      required: true
  - version:
      description: 'Initial version'
      type: string
      default: '0.1.0'
````

### Node.js API

REST API with Express.js:

```yaml
# Example: Node.js API
# Use case: Express.js REST API with proper structure

files:
  - package.json:
      content: |
        {
          "name": "{{@ package_name @}}",
          "version": "{{@ version | default('1.0.0') @}}",
          "description": "{{@ description @}}",
          "main": "src/app.js",
          "scripts": {
            "start": "node src/app.js",
            "dev": "nodemon src/app.js",
            "test": "jest"
          },
          "dependencies": {
            "express": "^4.18.0",
            "cors": "^2.8.5",
            "helmet": "^6.0.0",
            "dotenv": "^16.0.0"
          },
          "devDependencies": {
            "nodemon": "^2.0.20",
            "jest": "^29.0.0",
            "supertest": "^6.3.0"
          }
        }

  - src/app.js:
      content: |
        const express = require('express');
        const cors = require('cors');
        const helmet = require('helmet');
        require('dotenv').config();

        const app = express();
        const PORT = process.env.PORT || 3000;

        // Middleware
        app.use(helmet());
        app.use(cors());
        app.use(express.json());

        // Routes
        app.get('/', (req, res) => {
          res.json({ message: 'Welcome to {{@ project_name @}} API' });
        });

        app.get('/api/health', (req, res) => {
          res.json({ status: 'OK', timestamp: new Date().toISOString() });
        });

        app.listen(PORT, () => {
          console.log(`{{@ project_name @}} API running on port ${PORT}`);
        });

        module.exports = app;

  - .env.example:
      content: |
        PORT=3000
        NODE_ENV=development

variables:
  - project_name:
      description: 'Project name'
      type: string
      required: true
  - package_name:
      description: 'NPM package name'
      type: string
      required: true
  - description:
      description: 'API description'
      type: string
      required: true
  - version:
      description: 'Initial version'
      type: string
      default: '1.0.0'
```

## Usage

To use these examples:

1. **Copy the YAML content** from any example above
2. **Save it to a file** (e.g., `my-structure.yaml`)
3. **Run structkit generate** with your file:

```bash
# Create your structure file
cat > my-structure.yaml << 'EOF'
# Paste the YAML content here
EOF

# Generate your project
structkit generate file://my-structure.yaml ./my-project
```

### Quick Start with Template Variables

```bash
# Generate with custom variables
structkit generate -v "project_name=MyApp,author=John Doe" file://my-structure.yaml ./my-project
```

## Contributing Examples

We welcome community examples! To contribute:

1. Create a new `.yaml` file in this directory
2. Follow the naming convention: `descriptive-name.yaml`
3. Include comments explaining key concepts
4. Add the example to this index
5. Submit a pull request

### Example Template

```yaml
# Example: [Brief Description]
# Use case: [What this example demonstrates]
# Requirements: [Any prerequisites or dependencies]

files:
  - README.md:
      content: |
        # Example Project
        This demonstrates [key concept]

variables:
  - example_var:
      description: 'Example variable'
      type: string
      default: 'example_value'
```
