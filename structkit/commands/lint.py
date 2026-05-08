import json
import os
import re
from dataclasses import asdict, dataclass

import yaml
from jinja2 import Environment, TemplateSyntaxError, meta

from structkit.commands import Command
from structkit.commands.validate import ValidateCommand


class _NoopLogger:
    def info(self, *_args, **_kwargs):
        pass


@dataclass
class LintIssue:
    severity: str
    rule: str
    message: str
    path: str
    context: str = ""


class LintCommand(Command):
    """Lint StructKit YAML files for quality issues beyond schema validity."""

    STABLE_GIT_REF_RE = re.compile(r"^[0-9a-f]{40}$|^v?\d+\.\d+(?:\.\d+)?(?:[-+][0-9A-Za-z.-]+)?$")
    SUSPICIOUS_HOOK_PATTERNS = [
        re.compile(r"\bcurl\b.*\|\s*(?:ba)?sh\b"),
        re.compile(r"\bwget\b.*\|\s*(?:ba)?sh\b"),
        re.compile(r"\beval\b"),
        re.compile(r"\bchmod\s+777\b"),
        re.compile(r"\bsudo\b"),
    ]
    UNSAFE_HOOK_PATTERNS = [
        re.compile(r"\brm\s+-rf\s+/(?:\s|$)"),
        re.compile(r"\brm\s+-rf\s+\$\{?\w+\}?"),
        re.compile(r":\(\)\s*\{\s*:\|:"),
    ]
    REMOTE_URL_RE = re.compile(r"https?://[^\s'\"]+")
    NAME_RE = re.compile(r"^[A-Za-z0-9._@{}%/+=, -]+$")

    def __init__(self, parser):
        super().__init__(parser)
        parser.description = "Lint StructKit YAML definitions for quality issues"
        target = parser.add_argument(
            'targets',
            nargs='*',
            help='YAML file paths, file:// URLs, or bundled/custom structure names to lint',
        )
        from structkit.completers import structures_completer
        target.completer = structures_completer
        parser.add_argument(
            '--all',
            action='store_true',
            help='Lint all bundled contrib structures plus custom structures when --structures-path is set',
        )
        parser.add_argument(
            '-s', '--structures-path',
            type=str,
            help='Path to custom structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
            default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None),
        )
        parser.add_argument('--json', action='store_true', help='Print machine-readable JSON output')
        parser.set_defaults(func=self.execute)

        self.template_env = Environment(
            trim_blocks=True,
            block_start_string='{%@',
            block_end_string='@%}',
            variable_start_string='{{@',
            variable_end_string='@}}',
            comment_start_string='{#@',
            comment_end_string='@#}',
        )
        self.template_env.globals.update({
            'current_repo': lambda: None,
            'uuid': lambda: None,
            'now': lambda: None,
            'env': lambda *_args, **_kwargs: None,
            'read_file': lambda *_args, **_kwargs: None,
        })
        self.template_env.filters.update({
            'latest_release': lambda value: value,
            'slugify': lambda value: value,
            'default_branch': lambda value: value,
            'to_yaml': lambda value: value,
            'from_yaml': lambda value: value,
            'to_json': lambda value: value,
            'from_json': lambda value: value,
        })

    def execute(self, args):
        targets = self._resolve_targets(args)
        issues = []

        if not targets:
            issues.append(LintIssue('error', 'missing-target', 'Provide at least one target or use --all.', '<args>'))
        for target in targets:
            issues.extend(self.lint_file(target))

        if args.json:
            self._print_json(issues)
        else:
            self._print_text(issues)

        if any(issue.severity == 'error' for issue in issues):
            raise SystemExit(1)

    def _contribs_path(self):
        this_file = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(this_file, '..', 'contribs')

    def _resolve_targets(self, args):
        if args.all:
            roots = [self._contribs_path()]
            if args.structures_path:
                roots.insert(0, args.structures_path)
            return self._find_yaml_files(roots)

        targets = []
        for target in args.targets:
            targets.append(self._resolve_target(target, args.structures_path))
        return targets

    def _find_yaml_files(self, roots):
        files = []
        seen = set()
        for root in roots:
            if not root or not os.path.exists(root):
                continue
            for dirpath, _, filenames in os.walk(root):
                for filename in filenames:
                    if filename.endswith(('.yaml', '.yml')):
                        path = os.path.join(dirpath, filename)
                        if path not in seen:
                            files.append(path)
                            seen.add(path)
        return sorted(files)

    def _resolve_target(self, target, structures_path=None):
        if target.startswith('file://'):
            return target[7:]
        if target.endswith(('.yaml', '.yml')) or os.path.exists(target):
            return target

        candidates = []
        if structures_path:
            candidates.append(os.path.join(structures_path, f'{target}.yaml'))
            candidates.append(os.path.join(structures_path, f'{target}.yml'))
        candidates.append(os.path.join(self._contribs_path(), f'{target}.yaml'))
        candidates.append(os.path.join(self._contribs_path(), f'{target}.yml'))
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return target

    def lint_file(self, path):
        issues = []
        if not os.path.exists(path):
            return [LintIssue('error', 'not-found', f'Could not find structure target: {path}', path)]

        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f) or {}
        except yaml.YAMLError as exc:
            return [LintIssue('error', 'invalid-yaml', f'YAML could not be parsed: {exc}', path)]
        except OSError as exc:
            return [LintIssue('error', 'read-error', f'File could not be read: {exc}', path)]

        if not isinstance(config, dict):
            return [LintIssue('error', 'invalid-root', 'Top-level YAML document must be a mapping.', path)]

        issues.extend(self._validate_baseline(config, path))
        issues.extend(self._check_description(config, path))
        issues.extend(self._check_duplicates(config, path))
        issues.extend(self._check_templates(config, path))
        issues.extend(self._check_hooks(config, path))
        issues.extend(self._check_remote_urls(config, path))
        issues.extend(self._check_names(config, path))
        return issues

    def _validate_baseline(self, config, path):
        validator = ValidateCommand.__new__(ValidateCommand)
        validator.logger = _NoopLogger()
        try:
            validator._validate_structure_config(config.get('structure') or config.get('files', []))
            validator._validate_folders_config(config.get('folders', []))
            validator._validate_variables_config(config.get('variables', []))
        except ValueError as exc:
            return [LintIssue('error', 'validate', str(exc), path)]
        return []

    def _check_description(self, config, path):
        description = config.get('description')
        if not isinstance(description, str) or not description.strip():
            return [LintIssue('warning', 'missing-description', 'Missing top-level description.', path)]
        return []

    def _check_duplicates(self, config, path):
        issues = []
        for section, rule in (('files', 'duplicate-file'), ('structure', 'duplicate-file'), ('folders', 'duplicate-folder')):
            seen = {}
            for index, item in enumerate(config.get(section, []) or []):
                if not isinstance(item, dict):
                    continue
                for name in item:
                    if name in seen:
                        issues.append(LintIssue('error', rule, f"Duplicate {section[:-1]} entry '{name}'.", path, f'{section}[{index}]'))
                    else:
                        seen[name] = index
        return issues

    def _check_templates(self, config, path):
        issues = []
        declared = self._declared_variables(config)
        referenced = set()
        for context, value in self._walk_strings(config, skip_keys={'variables'}):
            try:
                parsed = self.template_env.parse(value)
            except TemplateSyntaxError as exc:
                issues.append(LintIssue('error', 'template-syntax', f'Template syntax error: {exc.message}', path, context))
                continue
            referenced.update(meta.find_undeclared_variables(parsed))

        referenced -= {'mappings'}
        for name in sorted(referenced - declared):
            issues.append(LintIssue('error', 'undeclared-variable', f"Variable '{name}' is referenced but not declared.", path))
        for name in sorted(declared - referenced):
            issues.append(LintIssue('warning', 'unused-variable', f"Variable '{name}' is declared but never referenced.", path))
        return issues

    def _declared_variables(self, config):
        declared = set()
        for item in config.get('variables', []) or []:
            if isinstance(item, dict):
                declared.update(str(name) for name in item.keys())
        return declared

    def _walk_strings(self, value, context='', skip_keys=None):
        skip_keys = skip_keys or set()
        if isinstance(value, str):
            yield context, value
        elif isinstance(value, list):
            for index, item in enumerate(value):
                yield from self._walk_strings(item, f'{context}[{index}]', skip_keys)
        elif isinstance(value, dict):
            for key, item in value.items():
                key_context = f'{context}.{key}' if context else str(key)
                if key in skip_keys:
                    continue
                if isinstance(key, str):
                    yield key_context, key
                yield from self._walk_strings(item, key_context, skip_keys)

    def _check_hooks(self, config, path):
        issues = []
        for hook_key in ('pre_hooks', 'post_hooks'):
            for index, hook in enumerate(config.get(hook_key, []) or []):
                if not isinstance(hook, str):
                    continue
                context = f'{hook_key}[{index}]'
                if any(pattern.search(hook) for pattern in self.UNSAFE_HOOK_PATTERNS):
                    issues.append(LintIssue('error', 'unsafe-hook', 'Hook contains an unsafe destructive command.', path, context))
                elif any(pattern.search(hook) for pattern in self.SUSPICIOUS_HOOK_PATTERNS):
                    issues.append(LintIssue('warning', 'suspicious-hook', 'Hook contains a suspicious shell pattern; review before use.', path, context))
        return issues

    def _check_remote_urls(self, config, path):
        issues = []
        for context, value in self._walk_strings(config, skip_keys={'variables'}):
            for url in self.REMOTE_URL_RE.findall(value):
                if self._is_unpinned_url(url):
                    issues.append(LintIssue('warning', 'unpinned-remote-url', 'Remote URL does not appear pinned to a stable ref.', path, context))
        return issues

    def _is_unpinned_url(self, url):
        if 'github.com' not in url and 'raw.githubusercontent.com' not in url:
            return False
        if '/releases/download/' in url:
            return False
        raw_match = re.search(r'raw\.githubusercontent\.com/[^/]+/[^/]+/([^/]+)/', url)
        if raw_match:
            return not bool(self.STABLE_GIT_REF_RE.match(raw_match.group(1)))
        ref_match = re.search(r'[?&]ref=([^&]+)', url)
        if ref_match:
            return not bool(self.STABLE_GIT_REF_RE.match(ref_match.group(1)))
        return any(branch in url for branch in ('/main/', '/master/', '/HEAD/', '/develop/')) or not re.search(r'/[0-9a-f]{40}/|/v?\d+\.\d+', url)

    def _check_names(self, config, path):
        issues = []
        for section in ('files', 'structure', 'folders'):
            for index, item in enumerate(config.get(section, []) or []):
                if not isinstance(item, dict):
                    continue
                for name in item:
                    if name.startswith('/') or '..' in name.split('/'):
                        issues.append(LintIssue('error', 'invalid-name', f"Entry name '{name}' must be relative and stay within the target directory.", path, f'{section}[{index}]'))
                    elif '\\' in name or not self.NAME_RE.match(str(name)):
                        issues.append(LintIssue('warning', 'naming-convention', f"Entry name '{name}' uses unusual characters.", path, f'{section}[{index}]'))
        return issues

    def _print_json(self, issues):
        payload = {
            'summary': {
                'errors': sum(1 for issue in issues if issue.severity == 'error'),
                'warnings': sum(1 for issue in issues if issue.severity == 'warning'),
            },
            'issues': [asdict(issue) for issue in issues],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))

    def _print_text(self, issues):
        if not issues:
            print('✅ No lint issues found.')
            return

        for issue in issues:
            label = 'ERROR' if issue.severity == 'error' else 'WARN'
            context = f' [{issue.context}]' if issue.context else ''
            print(f'{label} {issue.path}{context}: {issue.message} ({issue.rule})')
        errors = sum(1 for issue in issues if issue.severity == 'error')
        warnings = sum(1 for issue in issues if issue.severity == 'warning')
        print(f'\nLint summary: {errors} error(s), {warnings} warning(s).')
