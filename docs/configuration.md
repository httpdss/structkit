# Configuration

## Config Layering

Structkit supports a layered configuration system that allows you to set defaults at multiple levels. Configuration values are merged in the following order (from lowest to highest priority):

1. **Built-in defaults** - Hard-coded defaults that are always present
2. **User config** - Global defaults from `~/.config/struct/config.yaml`
3. **Project config** - Project-specific config from `.structkit.yaml` (legacy `.struct.yaml`) or `--config-file`
4. **CLI arguments** - Command-line flags (highest priority)

### User Config

You can create a user-level config file at `~/.config/struct/config.yaml` to set your personal defaults. This is useful for setting preferences that apply across all your projects.

Example `~/.config/struct/config.yaml`:

```yaml
structures_path: ~/my-custom-structures
input_store: ~/.cache/structkit/input.json
file_strategy: backup
log: WARNING
```

### Project Config

Project-specific settings can be defined in a `.structkit.yaml` file or specified via the `--config-file` flag. These settings override user config and built-in defaults. A legacy `.struct.yaml` file is still accepted when `.structkit.yaml` is not present.

### CLI Arguments

Command-line arguments always take the highest priority and override all config file settings.

### Supported Config Options

The following options can be configured via config files:

- `structures_path` - Path to custom structure definitions
- `source` - Named source for structure definitions
- `input_store` - Path to the input store file
- `file_strategy` - Strategy for handling existing files (`overwrite`, `skip`, `append`, `rename`, `backup`)
- `backup` - Path to backup folder
- `global_system_prompt` - Global system prompt for OpenAI
- `non_interactive` - Run in non-interactive mode (boolean)
- `output` - Output mode (`file` or `console`)
- `log` - Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- `log_file` - Path to log file

### Viewing Effective Configuration

To see the final merged configuration that structkit will use, run:

```bash
structkit config print
```

This displays the effective configuration after all layers have been merged. You can also output in JSON format:

```bash
structkit config print --format json
```

Example output:

```yaml
backup: null
file_strategy: backup
global_system_prompt: null
input_store: /tmp/structkit/input.json
log: INFO
log_file: null
non_interactive: false
output: file
source: null
structures_path: /home/user/my-structures
```

The command also displays which configuration sources were used:

```
Configuration sources:
  1. Built-in defaults: always loaded
  2. User config: /home/user/.config/struct/config.yaml (exists)
  3. Project config: .structkit.yaml
  4. CLI arguments: highest priority
```

## YAML Configuration Properties

When defining your project structure in the YAML configuration file, you can use various properties to control the behavior of the script. Here are the available properties:

- **skip**: If set to `true`, the file or folder will be skipped and not created.
- **skip_if_exists**: If set to `true`, the file or folder will be skipped if it already exists.
- **permissions**: Set custom file permissions using a string representation of the octal value (e.g., `'0777'`).
- **content**: Define the content of the file directly in the YAML configuration.
- **file**: Specify a local or remote file to include. Supported protocols include `file://`, `http://`, `https://`, `github://`, `githubhttps://`, `githubssh://`, `s3://`, and `gs://`.

  > **Note**: For local `.yaml` files, the `file://` protocol is automatically added if not specified.

Example:

```yaml
files:
  - README.md:
      skip: true
      content: |
        # {{@ project_name @}}
        This is a template repository.
  - script.sh:
      skip_if_exists: true
      permissions: '0777'
      content: |
        #!/bin/bash
        echo "Hello, {{@ author_name @}}!"
  - LICENSE:
      file: https://raw.githubusercontent.com/nishanths/license/master/LICENSE
  - remote_file.txt:
      file: file:///path/to/local/file.txt
  - github_file.py:
      file: github://owner/repo/branch/path/to/file.py
  - github_https_file.py:
      file: githubhttps://owner/repo/branch/path/to/file.py
  - github_ssh_file.py:
      file: githubssh://owner/repo/branch/path/to/file.py
  - s3_file.txt:
      file: s3://bucket_name/key
  - gcs_file.txt:
      file: gs://bucket_name/key
  - src/main.py:
      content: |
        print("Hello, World!")
folders:
  - .devops/modules/mod1:
      struct: terraform/module
  - .devops/modules/mod2:
      struct: terraform/module
      with:
        module_name: mymod2
  - ./:
      struct:
        - docker-files
        - project/go
variables:
  - project_name:
      description: "The name of the project"
      default: "MyProject"
      type: string
  - author_name:
      description: "The name of the author"
      type: string
      default: "John Doe"
```

These properties allow you to customize the behavior and content of the files and folders generated by the script, providing flexibility and control over your project structure.

### Template Variables

You can use template variables in your configuration file by enclosing them in `{{@` and `@}}`. For example, `{{@ project_name @}}` will be replaced with the value of the `project_name` variable at runtime. If this are not set when running the script, it will prompt you to enter the value interactively.

If you need to define blocks you can use starting block notation `{%@` and end block notation `@%}`.

To define comments you can use the comment start notation `{#@` and end comment notation `@#}`.

#### Default template variables

- `file_name`: The name of the file being processed.
- `file_directory`: The name of the directory of file that is being processed.

#### Interactive template variables

If you don't provide a default value for a variable, the script will prompt you to enter the value interactively.

The structkit defined should define the variable on a specific section of the YAML file. For example:

```yaml
variables:
  - author_name:
      description: "The name of the author"
      type: string
      default: "John Doe"
```

as you can see, the `author_name` variable is defined on the `variables` section of the YAML file. it includes a `description`, `type` and `default` value which is used if the user doesn't provide a value interactively.

#### Custom Jinja2 filters

##### `latest_release`

This filter selects the latest GitHub release for a repository. Its signature is:

```python
latest_release(repo_name: str, strip_v: bool = False, return_sha: bool = False) -> str
```

| Parameter | Type | Default | Behavior |
| --- | --- | --- | --- |
| `repo_name` | `str` | required | GitHub repository in `owner/name` form. |
| `strip_v` | `bool` | `false` | In version mode, remove exactly one leading lowercase `v` from the release tag. Tags without that prefix, including an uppercase `V`, are unchanged. |
| `return_sha` | `bool` | `false` | Return the commit SHA identified by the release tag instead of the tag name. |

Both options are optional, so existing calls keep their original behavior. For a latest release tagged `v3.2.1`, these examples produce:

```yaml
files:
  - release.txt:
      content: |
        # v3.2.1 (unchanged default output)
        {{@ "httpdss/structkit" | latest_release @}}

        # 3.2.1 (strip one leading lowercase "v")
        {{@ "httpdss/structkit" | latest_release(strip_v=true) @}}

        # 0123456789abcdef0123456789abcdef01234567 (release commit)
        {{@ "httpdss/structkit" | latest_release(return_sha=true) @}}
```

`return_sha=true` takes precedence when both options are enabled. In that case the filter returns the same commit SHA as `return_sha=true` alone; `strip_v` has no effect on a SHA.

The SHA is resolved from the Git tag reference. Lightweight tags resolve directly, while annotated tags are peeled until a commit is reached. Resolution examines at most 10 Git objects, so no more than nine annotated-tag hops may precede the final commit. The returned object ID must be a full 40-character SHA-1 or 64-character SHA-256 hexadecimal value. If a release was selected but its tag is missing, malformed, too deeply nested, cyclic, or does not resolve to a commit, the filter returns `LATEST_RELEASE_ERROR` rather than a tag-object SHA or an unrelated branch SHA.

If repository lookup succeeds but latest-release lookup fails, the established fallback remains the repository's default branch name. In SHA mode, the fallback is instead that branch's head commit SHA. `strip_v` is not applied to a fallback branch name. If repository lookup or fallback resolution fails, the result is `LATEST_RELEASE_ERROR`.

This filter uses PyGithub. Set the `GITHUB_TOKEN` environment variable to access private repositories and to receive authenticated API rate limits.

You can also use it with Terraform provider repositories, for example `{{@ "hashicorp/terraform-provider-aws" | latest_release(strip_v=true) @}}` or `{{@ "DataDog/terraform-provider-datadog" | latest_release(return_sha=true) @}}`.

##### `slugify`

This filter converts a string into a slug. It takes no arguments: the value is lowercased, runs of whitespace become a single hyphen, and any character that is not `a-z`, `0-9`, or `-` is removed.

```yaml
files:
  - README.md:
      content: |
        # {{@ project_name @}}
        This is a template repository.
        slugify project_name: {{@ project_name | slugify @}}
```

Note that underscores are removed rather than converted, so `My_Project` becomes `myproject`. To produce a different separator, chain Jinja2's built-in `replace` filter:

```yaml
files:
  - src/{{@ project_name | slugify | replace("-", "_") @}}/__init__.py:
      content: ""
```

##### `default_branch`

This filter fetches the default branch name of a GitHub repository. It takes the repository name as an argument.

```yaml
files:
  - README.md:
      content: |
        # MyProject
        Default branch: {{@ "httpdss/structkit" | default_branch @}}
```
