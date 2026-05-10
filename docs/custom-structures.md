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

## Named custom sources

StructKit can store named local structure sources in a user-level config file. This is useful when you reuse a shared template directory and do not want to pass `--structures-path` or set `STRUCTKIT_STRUCTURES_PATH` every time.

```bash
structkit sources add company ./templates
structkit sources list
structkit sources show company
structkit sources validate company
structkit sources remove company
```

By default, sources are written to `$XDG_CONFIG_HOME/structkit/sources.yaml` or `~/.config/structkit/sources.yaml`. Set `STRUCTKIT_SOURCES_CONFIG` to use a different file, or pass `structkit sources --config-path <file>`.

Named sources currently support local filesystem directories. Remote URLs are reserved for future support and are rejected by validation.

Use a source explicitly with `--source`:

```bash
structkit list --source company
structkit generate --source company project/python ./app
```

You can also prefix a structure definition with the source name:

```bash
structkit generate company/project/python ./app
```

Source resolution precedence is:

1. `--structures-path` (or `STRUCTKIT_STRUCTURES_PATH`, because it populates the same CLI option)
2. `--source` or a `<source>/<structure>` prefix
3. Built-in StructKit structures

This preserves existing `STRUCTKIT_STRUCTURES_PATH` behavior and leaves `generate` and `list` unchanged unless a named source is selected.
