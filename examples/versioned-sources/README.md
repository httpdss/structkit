# Versioned Sources Example

This example shows how a committed `.struct.yaml` can define its own named source and then reference structs from that source.

The example uses a local source so it works offline:

```yaml
sources:
  platform:
    path: examples/versioned-sources/structures
```

In a real shared-struct repository, pin the source to a tag or commit SHA instead:

```yaml
sources:
  platform:
    url: github://httpdss/platform-structures@v1.2.0/structures
```

or, for branch names that contain slashes:

```yaml
sources:
  platform:
    url: github://httpdss/platform-structures/structures?ref=release/1.x
```

## What it demonstrates

- `platform/app/base` resolves through the file-local `platform` source.
- `app/base.yaml` references `app/ci` without a source prefix.
- The nested `app/ci` reference inherits the same `platform` source context.
- A future change to the user's global `structkit sources` config will not affect this `.struct.yaml` file.

## Run it

From the StructKit repository root:

```bash
structkit generate examples/versioned-sources/.struct.yaml /tmp/structkit-versioned-sources-demo
```

Expected generated files:

```text
/tmp/structkit-versioned-sources-demo/README.md
/tmp/structkit-versioned-sources-demo/pyproject.toml
/tmp/structkit-versioned-sources-demo/.github/workflows/ci.yml
```

Preview without writing files:

```bash
structkit generate examples/versioned-sources/.struct.yaml /tmp/structkit-versioned-sources-demo --dry-run --diff
```
