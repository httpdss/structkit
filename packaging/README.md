# Linux Distribution Packages

This directory contains the configuration and tooling for building `.deb` (Debian/Ubuntu) and `.rpm` (Fedora/RHEL) packages for the structkit CLI.

## Package Structure

- `debian/` — Debian/Ubuntu package configuration
- `rpm/` — Fedora/RHEL package configuration
- `structkit-shim.sh` — Wrapper script installed at `/usr/bin/structkit`

## Architecture

The packages install structkit in a vendored Python virtual environment to handle dependencies that may not be available in distribution repositories:

- **Vendored environment**: `/usr/lib/structkit/venv/` — Complete Python environment with all dependencies
- **CLI wrapper**: `/usr/bin/structkit` — Shim script that invokes the vendored structkit
- **Documentation**: `/usr/share/doc/structkit/` — README and LICENSE files

This approach ensures:
- No conflicts with system Python packages
- Consistent dependency versions across distributions
- Simple installation without requiring pip or virtual environment management

## Building Packages Locally

### Prerequisites

Install required tools:

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-virtualenv
```

**Fedora/RHEL:**
```bash
sudo dnf install -y python3 python3-pip python3-virtualenv
```

**Install nfpm** (cross-platform package builder):
```bash
# Option 1: Using apt (Debian/Ubuntu)
echo "deb [trusted=yes] https://repo.goreleaser.com/apt/ /" | sudo tee /etc/apt/sources.list.d/goreleaser.list
sudo apt-get update
sudo apt-get install -y nfpm

# Option 2: Using yum/dnf (Fedora/RHEL)
echo '[goreleaser]
name=GoReleaser
baseurl=https://repo.goreleaser.com/yum/
enabled=1
gpgcheck=0' | sudo tee /etc/yum.repos.d/goreleaser.repo
sudo dnf install -y nfpm

# Option 3: Direct download
# See: https://nfpm.goreleaser.com/install/
```

### Build Steps

1. **Install Python build dependencies:**
   ```bash
   python3 -m pip install --upgrade pip build virtualenv
   ```

2. **Build the Python wheel:**
   ```bash
   python3 -m build --wheel
   ```

3. **Create vendored virtual environment:**
   ```bash
   mkdir -p dist
   python3 -m virtualenv dist/venv
   dist/venv/bin/pip install --upgrade pip
   dist/venv/bin/pip install dist/*.whl
   ```

4. **Build Debian package (amd64):**
   ```bash
   VERSION=$(python3 -c "import tomllib; f = open('pyproject.toml', 'rb'); data = tomllib.load(f); f.close(); print(data['project']['version'])")
   ARCH=amd64 nfpm package --packager deb --config packaging/debian/nfpm.yaml --target dist/
   ```

5. **Build RPM package (amd64):**
   ```bash
   VERSION=$(python3 -c "import tomllib; f = open('pyproject.toml', 'rb'); data = tomllib.load(f); f.close(); print(data['project']['version'])")
   ARCH=amd64 nfpm package --packager rpm --config packaging/rpm/nfpm.yaml --target dist/
   ```

The built packages will be in the `dist/` directory:
- `structkit_${VERSION}_amd64.deb`
- `structkit-${VERSION}-1.x86_64.rpm`

## Installing Packages

Packages are attached to each [GitHub Release](https://github.com/httpdss/structkit/releases) starting with 3.3.1. Download the `.deb` / `.rpm` (and `SHA256SUMS`) from the release, or build them locally with the steps above.

### Debian/Ubuntu

```bash
# Download the .deb from the GitHub release, then:
sudo apt install ./structkit_VERSION_amd64.deb

# If there are dependency issues, resolve them with:
sudo apt-get install -f
```

### Fedora/RHEL

```bash
# Download the .rpm from the GitHub release, then:
sudo dnf install ./structkit-VERSION-1.x86_64.rpm

# Or using rpm directly:
sudo rpm -ivh structkit-VERSION-1.x86_64.rpm
```

### Verify Installation

After installation, verify that structkit is working:

```bash
structkit info
structkit --help
```

## CI/CD: GitHub Actions Workflow

The `.github/workflows/build-linux-packages.yaml` workflow automatically builds packages when:

1. **On release** — Triggered when a new GitHub release is published
2. **Manual dispatch** — Can be triggered from the Actions tab with a required `tag` input (for example `v3.3.1`) to rebuild that tag and attach packages to that release

The workflow:
- Checks out the release tag (or the `workflow_dispatch` tag)
- Builds packages for both `amd64` and `arm64` architectures
- Creates both `.deb` and `.rpm` packages (4 total artifacts)
- Uploads packages as GitHub Actions artifacts (90-day retention)
- Attaches the packages and a `SHA256SUMS` file to the corresponding GitHub Release

### Triggering a Manual Build

1. Go to **Actions** → **build-linux-packages**
2. Click **Run workflow**
3. Enter the release tag to backfill (for example `v3.3.1`)
4. Click **Run workflow**

### Downloading Built Packages

After the workflow completes, download packages from the [GitHub release](https://github.com/httpdss/structkit/releases) for that tag:

- `structkit_VERSION_amd64.deb` / `structkit_VERSION_arm64.deb`
- `structkit-VERSION-1.x86_64.rpm` / `structkit-VERSION-1.aarch64.rpm`
- `SHA256SUMS`

The same files are also available as Actions artifacts:

- `structkit-VERSION-amd64-deb`
- `structkit-VERSION-arm64-deb`
- `structkit-VERSION-amd64-rpm`
- `structkit-VERSION-arm64-rpm`

## Package Contents

Each package includes:

- `/usr/bin/structkit` — CLI entry point (wrapper script)
- `/usr/lib/structkit/venv/` — Vendored Python environment with:
  - Python interpreter
  - structkit and all dependencies
  - Site packages (PyYAML, requests, openai, jinja2, etc.)
- `/usr/share/doc/structkit/README.md` — Project README
- `/usr/share/doc/structkit/LICENSE` — Apache-2.0 License

## Maintenance

### Updating Package Metadata

Package metadata is defined in:
- `packaging/debian/nfpm.yaml` — Debian package configuration
- `packaging/rpm/nfpm.yaml` — RPM package configuration

Common fields to update:
- `maintainer` — Package maintainer contact
- `description` — Package description
- `depends` — Runtime dependencies
- `recommends` — Recommended packages

### Version Synchronization

The package version is automatically extracted from `pyproject.toml` during builds. Ensure the version in `pyproject.toml` is updated before building or releasing.

## Troubleshooting

### Package Installation Issues

If you encounter dependency issues:

**Debian/Ubuntu:**
```bash
sudo apt-get update
sudo apt-get install -f
```

**Fedora/RHEL:**
```bash
sudo dnf install ca-certificates
```

### CLI Not Working After Install

Verify the installation:
```bash
which structkit                    # Should show /usr/bin/structkit
ls -la /usr/lib/structkit/venv/    # Should show Python environment
/usr/lib/structkit/venv/bin/structkit --help  # Direct invocation
```

If the shim script fails, you can directly invoke:
```bash
/usr/lib/structkit/venv/bin/structkit [command]
```

## Future Enhancements

This is Phase 1 of Linux distribution packaging. Not included in this PR:

- Submission to Debian mentors or Fedora review
- PPA/COPR repository setup
- Official distribution repository inclusion
- Package signing/verification
- Marketplace/catalog integration

These may be addressed in future phases based on community adoption and requirements.
