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

StructKit can store named structure sources in a user-level config file. This is useful when you reuse a shared template directory or GitHub repository and do not want to pass `--structures-path` or set `STRUCTKIT_STRUCTURES_PATH` every time.

```bash
structkit sources add company ./templates
structkit sources add platform httpdss/platform-structures
structkit sources add versioned github://httpdss/platform-structures@v1/structures
structkit sources list
structkit sources show company
structkit sources validate company
structkit sources remove company
```

By default, sources are written to `$XDG_CONFIG_HOME/structkit/sources.yaml` or `~/.config/structkit/sources.yaml`. Set `STRUCTKIT_SOURCES_CONFIG` to use a different file, or pass `structkit sources --config-path <file>`.

Named sources support:

- Local filesystem directories, such as `./templates` or `~/platform/structures`
- GitHub shorthand, such as `httpdss/platform-structures`
- GitHub URLs, such as `github://httpdss/platform-structures` or `github://httpdss/platform-structures@v1/structures`
- Query-style refs for branch names that contain slashes, such as `github://httpdss/platform-structures/structures?ref=release/1.x`
- Git URLs, including HTTPS, SSH, and `file://` repositories

Git-backed sources are cloned into `$XDG_CACHE_HOME/structkit/sources` or `~/.cache/structkit/sources` by default. Set `STRUCTKIT_SOURCES_CACHE` to use a different cache directory. StructKit runs `git fetch` when a git-backed source is resolved or validated. Branch refs are checked out from `origin/<branch>`; tag and commit refs are checked out detached so tags and SHAs do not run `git pull`.

## File-local sources

Committed `.struct.yaml` files can declare their own named sources. This keeps generation portable and protects existing files from changes to a user's global `structkit sources` configuration.

```yaml
sources:
  platform:
    url: github://httpdss/platform-structures@v1.2.0/structures

folders:
  - ./:
      struct: platform/python/service
      with:
        service_name: demo-api
```

File-local sources override user-level sources with the same name at the top level. Nested structs inherit the parent's source context, and a nested struct cannot silently redefine an inherited source name to a different URL/path. Use a different source name when you intentionally need two versions:

```yaml
sources:
  platform_v1:
    url: github://httpdss/platform-structures@v1/structures
  platform_v2:
    url: github://httpdss/platform-structures@v2/structures

folders:
  - ./:
      struct:
        - platform_v1/python/service
        - platform_v2/github/actions-ci
```

Unqualified nested structs inherit the current structures path. For example, if `platform/python/service` references `github/actions-ci`, that child struct is resolved from the same pinned `platform` source unless it uses another named source or a fully qualified remote reference.

You can also reference a remote struct directly:

```yaml
folders:
  - ./:
      struct: github://httpdss/platform-structures@v1.2.0/structures/python/service
```

For reproducible `.struct.yaml` files, prefer tags or commit SHAs over mutable branches.

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
