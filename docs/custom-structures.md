# Creating Custom Structures

Let's say you are happy with the default structures that StructKit provides, but you want to customize them for your specific needs. This is totally possible!

The best way to approach this is to have a repository where you can store your custom structures. You can then reference these structures in your `.struct.yaml` files.

## Suggested Repository Structure

Here is a suggested structure for your custom structures repository:

```sh
structures/
├── category1/
│   ├── structure1.yaml
│   └── structure2.yaml
├── category2/
│   ├── structure1.yaml
│   └── structure2.yaml
```

This way you could reference your custom structures in your `.struct.yaml` files like this:

```yaml
folders:
  - ./:
    struct:
      - category1/structure1
      - category2/structure2
    with:
      var_in_structure1: 'value'
```

For this to work, you will need to set the path to the custom structures repository using the `-s` option when running StructKit:

```sh
structkit generate -s ~/path/to/custom-structures/structures file://.struct.yaml ./output
```

## Named Sources

You can save frequently used custom structure directories as named sources with the `structkit sources` command group. Sources are stored in a user-level StructKit config file at `~/.config/structkit/sources.json` by default. Automation and tests can override that location with `STRUCTKIT_SOURCES_CONFIG`.

```sh
structkit sources add company ~/path/to/custom-structures/structures
structkit sources list
structkit sources show company
structkit sources validate company
structkit sources remove company
```

Named sources currently support local filesystem directories. Remote URLs are reserved for future support.

After a source is configured, select it explicitly with `--source`:

```sh
structkit list --source company
structkit search --source company python
structkit info --source company project/python
structkit generate --source company project/python ./output
```

For `generate` and `info`, you can also prefix the structure name with a configured source name:

```sh
structkit generate company/project/python ./output
```

### Precedence and compatibility

Existing custom-structure behavior remains compatible:

1. `--structures-path` and `STRUCTKIT_STRUCTURES_PATH` point commands at a custom directory.
2. If no structures path is set, `--source <name>` selects a named source.
3. If no structures path or `--source` is set, `generate` and `info` can resolve source-prefixed names such as `company/project/python`.
4. If none of the above are used, StructKit uses its bundled contrib structures.

When a custom path or named source is selected, StructKit still falls back to bundled contrib structures for `list`, `search`, and `generate` in the same way as the existing `STRUCTKIT_STRUCTURES_PATH` workflow.
