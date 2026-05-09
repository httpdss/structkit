import json
import os
import re
from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

import yaml
from jinja2 import Environment, TemplateSyntaxError, meta

from structkit.commands import Command
from structkit.completers import structures_completer


@dataclass
class LintIssue:
  severity: str
  rule: str
  message: str
  file: str
  context: str = ""


class LintCommand(Command):
    """Run structure quality checks on StructKit YAML definitions."""

    TEMPLATE_GLOBALS = {
      'current_repo',
      'env',
      'mappings',
      'now',
      'read_file',
      'uuid',
    }
    VARIABLE_NAME_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
    STABLE_REF_RE = re.compile(r'^[a-f0-9]{40}$|^v?\d+(?:\.\d+){1,3}(?:[-+][A-Za-z0-9_.-]+)?$')

    def __init__(self, parser):
      super().__init__(parser)
      parser.description = "Lint StructKit YAML files for quality and safety issues"
      target_arg = parser.add_argument(
        'targets',
        nargs='*',
        help='YAML file paths or structure names to lint',
      )
      target_arg.completer = structures_completer
      parser.add_argument(
        '-s',
        '--structures-path',
        type=str,
        help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
        default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None),
      )
      parser.add_argument('--all', action='store_true', help='Lint all bundled contrib structures')
      parser.add_argument('--json', action='store_true', help='Output lint results as JSON')
      parser.set_defaults(func=self.execute)

      self.env = Environment(
        trim_blocks=True,
        block_start_string='{%@',
        block_end_string='@%}',
        variable_start_string='{{@',
        variable_end_string='@}}',
        comment_start_string='{#@',
        comment_end_string='@#}',
      )
      # Register lightweight stand-ins so Jinja can parse StructKit templates
      # during static analysis without executing any helper/filter logic.
      self.env.filters.update({
        'default_branch': lambda value: value,
        'from_json': lambda value: value,
        'from_yaml': lambda value: value,
        'latest_release': lambda value: value,
        'slugify': lambda value: value,
        'to_json': lambda value: value,
        'to_yaml': lambda value: value,
      })
      self.env.globals.update({name: None for name in self.TEMPLATE_GLOBALS})

    def execute(self, args):
      results = self.lint(args.targets, structures_path=args.structures_path, lint_all=args.all)
      if args.json:
        print(json.dumps(results, indent=2))
      else:
        self._print_text(results)

      if results['summary']['errors'] > 0:
        raise SystemExit(1)

    def lint(
      self,
      targets: Optional[Sequence[str]],
      structures_path: Optional[str] = None,
      lint_all: bool = False,
    ) -> Dict[str, Any]:
      files = self._resolve_targets(targets or [], structures_path, lint_all)
      issues: List[LintIssue] = []

      if not files:
        issues.append(LintIssue(
          'error',
          'target-required',
          'Provide one or more YAML files, structure names, or --all.',
          '',
        ))

      for file_path in files:
        issues.extend(self._lint_file(file_path))

      error_count = sum(1 for issue in issues if issue.severity == 'error')
      warning_count = sum(1 for issue in issues if issue.severity == 'warning')
      return {
        'summary': {
          'files': len(files),
          'errors': error_count,
          'warnings': warning_count,
        },
        'issues': [asdict(issue) for issue in issues],
      }

    def _resolve_targets(
      self,
      targets: Sequence[str],
      structures_path: Optional[str],
      lint_all: bool,
    ) -> List[str]:
      files: List[str] = []
      seen: Set[str] = set()

      def add(path: str):
        full = os.path.abspath(path)
        if full not in seen:
          seen.add(full)
          files.append(full)

      if lint_all:
        for root, _, names in os.walk(self._contribs_path()):
          for name in names:
            if name.endswith(('.yaml', '.yml')):
              add(os.path.join(root, name))

      for target in targets:
        resolved = self._resolve_target(target, structures_path)
        add(resolved)

      return files

    def _resolve_target(self, target: str, structures_path: Optional[str]) -> str:
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
      return candidates[0] if candidates else target

    def _contribs_path(self) -> str:
      this_file = os.path.dirname(os.path.realpath(__file__))
      return os.path.normpath(os.path.join(this_file, '..', 'contribs'))

    def _lint_file(self, file_path: str) -> List[LintIssue]:
      issues: List[LintIssue] = []
      if not os.path.exists(file_path):
        return [LintIssue('error', 'file-not-found', f'File not found: {file_path}', file_path)]

      try:
        with open(file_path, 'r') as handle:
          config = yaml.safe_load(handle) or {}
      except yaml.YAMLError as exc:
        return [LintIssue('error', 'invalid-yaml', f'Invalid YAML: {exc}', file_path)]
      except OSError as exc:
        return [LintIssue('error', 'read-error', f'Failed to read file: {exc}', file_path)]

      if not isinstance(config, dict):
        return [LintIssue('error', 'top-level-mapping', 'Top-level YAML content must be a mapping.', file_path)]

      if not str(config.get('description') or '').strip():
        issues.append(LintIssue('warning', 'missing-description', 'Missing top-level description.', file_path))

      declared_vars, variable_issues = self._declared_variables(config, file_path)
      issues.extend(variable_issues)

      references, reference_issues = self._referenced_variables(config, file_path)
      issues.extend(reference_issues)
      for name in sorted(references - declared_vars - self.TEMPLATE_GLOBALS):
        issues.append(LintIssue(
          'error',
          'undefined-variable',
          f"Template references variable '{name}' but it is not declared.",
          file_path,
        ))
      for name in sorted(declared_vars - references):
        issues.append(LintIssue(
          'warning',
          'unused-variable',
          f"Variable '{name}' is declared but never referenced.",
          file_path,
        ))

      issues.extend(self._duplicate_entry_issues(config, file_path))
      issues.extend(self._hook_issues(config, file_path))
      issues.extend(self._remote_url_issues(config, file_path))
      return issues

    def _declared_variables(self, config: Dict[str, Any], file_path: str) -> Tuple[Set[str], List[LintIssue]]:
      variables = config.get('variables', []) or []
      declared: Set[str] = set()
      issues: List[LintIssue] = []
      if not isinstance(variables, list):
        return declared, [LintIssue('error', 'invalid-variables', "The 'variables' key must be a list.", file_path)]

      for item in variables:
        if not isinstance(item, dict):
          issues.append(LintIssue('error', 'invalid-variable-entry', 'Each variable entry must be a mapping.', file_path))
          continue
        if isinstance(item.get('name'), str):
          names = [item['name']]
        else:
          names = list(item.keys())
        for name in names:
          if not isinstance(name, str):
            issues.append(LintIssue('error', 'invalid-variable-name', 'Variable names must be strings.', file_path))
            continue
          if name in declared:
            issues.append(LintIssue('error', 'duplicate-variable', f"Variable '{name}' is declared more than once.", file_path))
          declared.add(name)
          if not self.VARIABLE_NAME_RE.match(name):
            issues.append(LintIssue(
              'warning',
              'naming-convention',
              f"Variable '{name}' should use a Python/Jinja-friendly identifier name.",
              file_path,
            ))
      return declared, issues

    def _referenced_variables(self, config: Dict[str, Any], file_path: str) -> Tuple[Set[str], List[LintIssue]]:
      references: Set[str] = set()
      issues: List[LintIssue] = []
      for context, value in self._template_values(config):
        try:
          parsed = self.env.parse(value)
          references.update(meta.find_undeclared_variables(parsed))
        except TemplateSyntaxError as exc:
          issues.append(LintIssue('error', 'template-syntax', f'Template syntax error: {exc}', file_path, context))
      return references, issues

    def _template_values(self, config: Dict[str, Any]) -> Iterable[Tuple[str, str]]:
      for key in ('files', 'structure'):
        for item in config.get(key, []) or []:
          if isinstance(item, dict):
            for path, content in item.items():
              yield f'{key}.{path}', str(path)
              yield from self._string_values(content, f'{key}.{path}')
          elif isinstance(item, str):
            yield key, item
      for item in config.get('folders', []) or []:
        if isinstance(item, dict):
          for path, content in item.items():
            yield f'folders.{path}', str(path)
            if isinstance(content, dict):
              yield from self._string_values(content.get('with', {}), f'folders.{path}.with')
        elif isinstance(item, str):
          yield 'folders', item
      for key in ('pre_hooks', 'post_hooks'):
        yield from self._string_values(config.get(key, []), key)

    def _string_values(self, value: Any, context: str) -> Iterable[Tuple[str, str]]:
      if isinstance(value, str):
        yield context, value
      elif isinstance(value, dict):
        for key, child in value.items():
          yield from self._string_values(child, f'{context}.{key}')
      elif isinstance(value, list):
        for index, child in enumerate(value):
          yield from self._string_values(child, f'{context}[{index}]')

    def _duplicate_entry_issues(self, config: Dict[str, Any], file_path: str) -> List[LintIssue]:
      issues: List[LintIssue] = []
      for key in ('files', 'structure', 'folders'):
        seen: Set[str] = set()
        for item in config.get(key, []) or []:
          if isinstance(item, dict):
            names = [str(name) for name in item.keys()]
          else:
            names = [str(item)]
          for name in names:
            normalized = os.path.normpath(name)
            if normalized in seen:
              issues.append(LintIssue('error', f'duplicate-{key}-entry', f"Duplicate {key} entry '{name}'.", file_path))
            seen.add(normalized)
      return issues

    def _hook_issues(self, config: Dict[str, Any], file_path: str) -> List[LintIssue]:
      issues: List[LintIssue] = []
      for key in ('pre_hooks', 'post_hooks'):
        hooks = config.get(key, []) or []
        if hooks and not isinstance(hooks, list):
          issues.append(LintIssue('error', 'invalid-hooks', f"The '{key}' key must be a list of shell commands.", file_path))
          continue
        for command in hooks:
          if not isinstance(command, str):
            issues.append(LintIssue('error', 'invalid-hook-command', f"Each item in '{key}' must be a string.", file_path))
            continue
          compact = re.sub(r'\s+', ' ', command.strip().lower())
          if re.search(r'\brm\s+-[a-z]*r[f]?\s+/(?:\s|$)', compact):
            issues.append(LintIssue('error', 'unsafe-hook', 'Hook appears to remove the filesystem root.', file_path, key))
          elif re.search(r'\b(curl|wget)\b.*\|\s*(sh|bash)\b', compact):
            issues.append(LintIssue('warning', 'suspicious-hook', 'Hook pipes remote content directly into a shell.', file_path, key))
          elif re.search(r'\b(eval|sudo)\b|chmod\s+777', compact):
            issues.append(LintIssue('warning', 'suspicious-hook', 'Hook uses a potentially risky shell operation.', file_path, key))
      return issues

    def _remote_url_issues(self, config: Dict[str, Any], file_path: str) -> List[LintIssue]:
      issues: List[LintIssue] = []
      for context, value in self._string_values(config, ''):
        if not isinstance(value, str) or not value.startswith(('http://', 'https://')):
          continue
        if self._is_unpinned_remote(value):
          issues.append(LintIssue(
            'warning',
            'unpinned-remote-url',
            f"Remote URL is not pinned to a stable ref: {value}",
            file_path,
            context,
          ))
      return issues

    def _is_unpinned_remote(self, url: str) -> bool:
      raw_match = re.search(r'raw\.githubusercontent\.com/[^/]+/[^/]+/([^/]+)/', url)
      if raw_match:
        return not self.STABLE_REF_RE.match(raw_match.group(1))
      github_blob = re.search(r'github\.com/[^/]+/[^/]+/(?:blob|raw)/([^/]+)/', url)
      if github_blob:
        return not self.STABLE_REF_RE.match(github_blob.group(1))
      return False

    def _print_text(self, results: Dict[str, Any]):
      summary = results['summary']
      print(f"Linted {summary['files']} file(s): {summary['errors']} error(s), {summary['warnings']} warning(s)")
      for issue in results['issues']:
        location = issue['file'] or '<input>'
        if issue.get('context'):
          location = f"{location} ({issue['context']})"
        print(f"{issue['severity'].upper()}: {location}: [{issue['rule']}] {issue['message']}")
