---
tags:
  - quickstart
  - docker
  - mcp
---

# Quick Start

## Quick Start Using Docker

1. Create a YAML configuration file for your project structure. [See sample configuration here](https://github.com/httpdss/structkit/blob/main/example/structure.yaml).
2. Run the following command to generate the project structure:

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/structkit:main generate \
  file:///workdir/example/structure.yaml \
  /workdir/example_output
```

## Quick Start Using Docker Alpine

```sh
docker run \
  -v $(pwd):/workdir \
  -u $(id -u):$(id -g) \
  ghcr.io/httpdss/structkit:alpine generate \
  file:///workdir/example/structure.yaml \
  /workdir/example_output
```

For testing, you can run an alpine Docker container and install the script inside it:

```sh
docker run -it --entrypoint="" python:3.10-alpine sh -l
```

Inside the container:

```sh
apk add python-pip git vim
pip install structkit
mkdir example
cd example/
touch structure.yaml
vim structure.yaml # copy the content from the example folder
structkit generate structure.yaml .
```

> Note: The `file://` protocol is automatically added for `.yaml` files, so `structure.yaml` and `file://structure.yaml` work identically. Additionally, if your file is named `.struct.yaml` in the current directory and you want to generate into the current directory, you can just run `structkit generate`.

## Discovering Available Structures

Before generating, see what structures are available:

```sh
structkit list
```

This shows all built-in structures you can use.

!!! tip "Auto-Completion"
    If you've enabled [auto-completion](completion.md), you can press `Tab` after `structkit generate` to see all available structures!

## First Example

After installing StructKit, try this simple example:

```sh
structkit generate terraform/modules/generic ./my-terraform-module
```

This will create a new terraform module structure in the `./my-terraform-module` directory.

Or try a simple project structure:

```sh
structkit generate project/nodejs ./my-node-app
```

## Bootstrap a new project

Start with a minimal .struct.yaml:

```sh
structkit init
```

This writes a basic .struct.yaml with hooks, a README, and a reference to the run-structkit workflow.

## Next Steps

- Learn about [YAML Configuration](configuration.md)
- Explore [Template Variables](template-variables.md)
- Check out [Usage Examples](usage.md)
