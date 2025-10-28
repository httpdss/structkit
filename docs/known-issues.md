# Known Issues

This page tracks known issues, limitations, and workarounds for StructKit. If you encounter any of these issues, check here for potential solutions.

## Current Known Issues

### Performance Issues

#### Large Directory Structures

**Issue**: Generation becomes slow with very large directory structures (1000+ files).

**Workaround**:

- Break large structures into smaller, modular components
- Use the `--dry-run` option to preview before full generation
- Consider using parallel processing for independent structures

**Status**: Under investigation

#### Remote File Fetching

**Issue**: Fetching many remote files can be slow due to sequential processing.

**Workaround**:

- Cache frequently used remote files locally
- Use local mirrors when possible
- Batch remote operations when feasible

**Status**: Planned for future release

### Template Engine

#### Complex Jinja2 Expressions

**Issue**: Very complex Jinja2 expressions may not render correctly in all contexts.

**Example**:

```yaml
# May not work as expected
content: "{{@ complex | filter | another_filter if condition else fallback @}}"
```

**Workaround**: Break complex expressions into simpler parts or use variables:

```yaml
variables:
  - intermediate_value:
      default: "{{@ complex | filter @}}"

files:
  - test.txt:
      content: "{{@ intermediate_value | another_filter @}}"
```

**Status**: Investigating improvements

#### Unicode in File Names

**Issue**: File names with unicode characters may cause issues on some filesystems.

**Workaround**: Use ASCII-safe file names or test thoroughly on target systems.

**Status**: Platform-specific limitation

### Platform-Specific Issues

#### Windows Path Handling

**Issue**: Long path names on Windows may exceed the 260-character limit.

**Workaround**:

- Use shorter path names
- Enable long path support in Windows 10/11
- Use mapped drives for shorter paths

**Status**: Windows limitation

#### macOS Case Sensitivity

**Issue**: macOS filesystem case-insensitivity can cause conflicts with similarly named files.

**Workaround**: Ensure file names differ by more than just case.

**Status**: Platform limitation

### GitHub Integration

#### Rate Limiting

**Issue**: GitHub API rate limits may affect custom filters like `latest_release`.

**Workaround**:

- Set `GITHUB_TOKEN` environment variable for higher limits
- Cache results when possible
- Implement retry logic in scripts

**Status**: API limitation

#### Private Repository Access

**Issue**: Accessing private repositories requires proper authentication.

**Workaround**: Ensure `GITHUB_TOKEN` has appropriate permissions.

**Status**: Expected behavior

### Docker Issues

#### File Permissions

**Issue**: Files created in Docker containers may have incorrect ownership.

**Workaround**: Use the `-u $(id -u):$(id -g)` option when running Docker:

```sh
docker run -v $(pwd):/workdir -u $(id -u):$(id -g) ghcr.io/httpdss/structkit:main generate file://config.yaml .
```

**Status**: Docker behavior

#### Volume Mounting

**Issue**: Complex volume mounting scenarios may not work as expected.

**Workaround**: Use simpler mounting patterns and absolute paths.

**Status**: Docker limitation

## Limitations

### Template Variables

#### Variable Scope

**Limitation**: Variables defined in nested structures don't propagate back to parent structures.

**Design Decision**: This is intentional to maintain structure isolation.

#### Circular References

**Limitation**: Circular references in variable definitions are not detected.

**Example**:

```yaml
variables:
  - var_a:
      default: "{{@ var_b @}}"
  - var_b:
      default: "{{@ var_a @}}"
```

**Impact**: May cause infinite loops or unexpected behavior.

### File Operations

#### Atomic Operations

**Limitation**: File operations are not atomic - partial failures may leave the system in an inconsistent state.

**Mitigation**: Use the `--backup` option for important operations.

#### Symlink Handling

**Limitation**: Symbolic links are not explicitly handled and may be followed or replaced.

**Impact**: May affect complex directory structures with symlinks.

### Configuration

#### YAML Complexity

**Limitation**: Very large YAML files (>10MB) may cause performance issues.

**Recommendation**: Split large configurations into multiple files.

#### Schema Validation

**Limitation**: Schema validation doesn't catch all runtime errors.

**Note**: Use `structkit validate` and testing for comprehensive validation.

## Workarounds and Best Practices

### Performance Optimization

1. **Use `--dry-run`** for testing large configurations
2. **Modularize structures** instead of creating monolithic ones
3. **Cache remote content** locally when possible
4. **Use specific structure paths** instead of recursive searches

### Error Prevention

1. **Validate configurations** before deployment
2. **Test with small datasets** first
3. **Use version control** for all configuration files
4. **Implement backup strategies** for important operations

### Cross-Platform Compatibility

1. **Test on target platforms** before deployment
2. **Use relative paths** when possible
3. **Avoid platform-specific commands** in hooks
4. **Document platform requirements** clearly

## Reporting Issues

### Before Reporting

1. Check this known issues page
2. Search existing GitHub issues
3. Test with the latest version
4. Prepare a minimal reproduction case

### Issue Report Template

```markdown
**StructKit Version**: [e.g., 1.2.3]
**Platform**: [e.g., Ubuntu 20.04, macOS 12.0, Windows 11]
**Python Version**: [e.g., 3.9.7]

**Expected Behavior**:
[Describe what you expected to happen]

**Actual Behavior**:
[Describe what actually happened]

**Reproduction Steps**:
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Configuration File**:

```yaml
[Paste minimal configuration that reproduces the issue]
```

**Error Output**:

```text
[Paste any error messages or logs]
```

**Additional Context**:

[Any other relevant information]

```text

### Priority Guidelines

- **Critical**: Security issues, data loss, system crashes
- **High**: Major functionality broken, widespread impact
- **Medium**: Minor functionality issues, workarounds available
- **Low**: Enhancement requests, documentation issues

## Contributing Fixes

We welcome contributions to fix known issues:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b fix/issue-name`
3. **Write tests** for your fix
4. **Update documentation** if necessary
5. **Submit a pull request**

### Testing Requirements

- All existing tests must pass
- New tests should cover the fixed functionality
- Manual testing on multiple platforms when applicable

## Version Compatibility

### Supported Versions

- **Latest release**: Full support and active development
- **Previous minor version**: Security fixes and critical bugs
- **Older versions**: Community support only

### Upgrade Recommendations

- Test upgrades in non-production environments first
- Review changelog for breaking changes
- Update configurations for deprecated features

---

*This page is updated regularly. Subscribe to repository notifications for updates on issue status.*
