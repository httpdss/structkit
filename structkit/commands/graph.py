from structkit.commands import Command
import json
import os
import yaml
from structkit.completers import structures_completer


class GraphCommand(Command):
  def __init__(self, parser):
    super().__init__(parser)
    parser.description = "Visualize structure dependencies"
    structure_arg = parser.add_argument(
      'structure_definition',
      nargs='?',
      type=str,
      help='Structure name or local YAML file to graph'
    )
    structure_arg.completer = structures_completer
    parser.add_argument(
      '--all',
      action='store_true',
      help='Graph all available structures'
    )
    parser.add_argument(
      '--format',
      choices=['text', 'json', 'mermaid'],
      default='text',
      help='Output format (default: text)'
    )
    parser.add_argument(
      '-s',
      '--structures-path',
      type=str,
      help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
      default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
    )
    parser.set_defaults(func=self.execute)

  def execute(self, args):
    self.logger.info("Building structure dependency graph")
    if not args.all and not args.structure_definition:
      self.parser.error("provide a structure name, local YAML file, or --all")

    graph = self.build_graph(args.structure_definition, args.structures_path, args.all)

    if args.format == 'json':
      print(self.format_json(graph))
    elif args.format == 'mermaid':
      print(self.format_mermaid(graph))
    else:
      print(self.format_text(graph))

  def build_graph(self, structure_definition=None, structures_path=None, include_all=False):
    roots = self._all_structure_names(structures_path) if include_all else [structure_definition]
    graph = {
      'roots': roots,
      'nodes': [],
      'edges': [],
      'missing': [],
      'cycles': [],
    }
    nodes = set()
    edges = set()
    missing = set()
    cycles = set()

    for root in roots:
      self._visit(root, structures_path, [], nodes, edges, missing, cycles)

    graph['nodes'] = sorted(nodes)
    graph['edges'] = [
      {'from': source, 'to': target}
      for source, target in sorted(edges)
    ]
    graph['missing'] = [
      {'from': source, 'to': target}
      for source, target in sorted(missing)
    ]
    graph['cycles'] = [list(cycle) for cycle in sorted(cycles)]
    return graph

  def format_json(self, graph):
    return json.dumps(graph, indent=2)

  def format_mermaid(self, graph):
    lines = ['graph TD']
    rendered_edges = set()

    for node in graph['nodes']:
      if not any(edge['from'] == node or edge['to'] == node for edge in graph['edges']):
        lines.append(f"  {self._mermaid_id(node)}[\"{self._escape_mermaid_label(node)}\"]")

    for edge in graph['edges']:
      rendered_edges.add((edge['from'], edge['to']))
      lines.append(
        f"  {self._mermaid_id(edge['from'])}[\"{self._escape_mermaid_label(edge['from'])}\"] --> "
        f"{self._mermaid_id(edge['to'])}[\"{self._escape_mermaid_label(edge['to'])}\"]"
      )

    for miss in graph['missing']:
      if (miss['from'], miss['to']) not in rendered_edges:
        lines.append(
          f"  {self._mermaid_id(miss['from'])}[\"{self._escape_mermaid_label(miss['from'])}\"] -. missing .-> "
          f"{self._mermaid_id(miss['to'])}[\"{self._escape_mermaid_label(miss['to'])}\"]"
        )
      lines.append(f"  class {self._mermaid_id(miss['to'])} missing")

    if graph['cycles']:
      cycle_nodes = sorted({node for cycle in graph['cycles'] for node in cycle})
      for node in cycle_nodes:
        lines.append(f"  class {self._mermaid_id(node)} cycle")

    lines.append('  classDef missing fill:#ffe6e6,stroke:#cc0000,color:#660000')
    lines.append('  classDef cycle fill:#fff4cc,stroke:#d19a00,color:#5c3b00')
    return '\n'.join(lines)

  def format_text(self, graph):
    lines = []
    for root in graph['roots']:
      self._append_tree(root, graph, lines, set(), '')

    if graph['missing']:
      lines.append('')
      lines.append('Missing references:')
      for miss in graph['missing']:
        lines.append(f"  - {miss['from']} -> {miss['to']}")

    if graph['cycles']:
      lines.append('')
      lines.append('Cycles:')
      for cycle in graph['cycles']:
        lines.append(f"  - {' -> '.join(cycle)}")

    return '\n'.join(lines)

  def _append_tree(self, node, graph, lines, stack, prefix='', child_prefix=''):
    label = node
    if node in stack:
      lines.append(f"{prefix}{label} (cycle)")
      return
    lines.append(f"{prefix}{label}")
    prefix = child_prefix

    children = sorted(edge['to'] for edge in graph['edges'] if edge['from'] == node)
    missing_children = sorted(miss['to'] for miss in graph['missing'] if miss['from'] == node)
    child_entries = [(child, False) for child in children] + [(child, True) for child in missing_children]
    next_stack = set(stack)
    next_stack.add(node)

    for index, (child, is_missing) in enumerate(child_entries):
      is_last = index == len(child_entries) - 1
      branch = '└── ' if is_last else '├── '
      continuation = '    ' if is_last else '│   '
      if is_missing:
        lines.append(f"{prefix}{branch}{child} (missing)")
      else:
        self._append_tree(child, graph, lines, next_stack, prefix + branch, prefix + continuation)

  def _visit(self, structure_definition, structures_path, stack, nodes, edges, missing, cycles):
    if structure_definition in stack:
      cycle = stack[stack.index(structure_definition):] + [structure_definition]
      cycles.add(tuple(cycle))
      nodes.add(structure_definition)
      return

    config = self._load_yaml_config(structure_definition, structures_path)
    if config is None:
      if stack:
        missing.add((stack[-1], structure_definition))
      else:
        missing.add((structure_definition, structure_definition))
      return

    nodes.add(structure_definition)
    next_stack = stack + [structure_definition]
    for dependency in self._extract_dependencies(config):
      if self._resolve_structure_path(dependency, structures_path) is None:
        missing.add((structure_definition, dependency))
        continue
      edges.add((structure_definition, dependency))
      self._visit(dependency, structures_path, next_stack, nodes, edges, missing, cycles)

  def _extract_dependencies(self, config):
    dependencies = []
    for item in config.get('folders', []) or []:
      if not isinstance(item, dict):
        continue
      for _, content in item.items():
        if not isinstance(content, dict) or 'struct' not in content:
          continue
        struct_value = content['struct']
        if isinstance(struct_value, list):
          dependencies.extend(str(struct) for struct in struct_value)
        elif isinstance(struct_value, str):
          dependencies.append(struct_value)
    return dependencies

  def _load_yaml_config(self, structure_definition, structures_path):
    path = self._resolve_structure_path(structure_definition, structures_path)
    if not path or not os.path.exists(path):
      self.logger.error(f"❗ File not found for structure: {structure_definition}")
      return None
    with open(path, 'r') as f:
      return yaml.safe_load(f) or {}

  def _resolve_structure_path(self, structure_definition, structures_path):
    if not structure_definition:
      return None

    if structure_definition.startswith('file://'):
      return structure_definition[7:]

    if structure_definition.endswith('.yaml') and os.path.exists(structure_definition):
      return structure_definition

    for base_path in self._structure_paths(structures_path):
      file_path = os.path.join(base_path, f"{structure_definition}.yaml")
      if os.path.exists(file_path):
        return file_path

    return None

  def _all_structure_names(self, structures_path):
    structures = set()
    for base_path in self._structure_paths(structures_path):
      if not os.path.exists(base_path):
        continue
      for root, _, files in os.walk(base_path):
        for file in files:
          if file.endswith('.yaml'):
            file_path = os.path.join(root, file)
            structures.add(os.path.relpath(file_path, base_path)[:-5])
    return sorted(structures)

  def _structure_paths(self, structures_path):
    this_file = os.path.dirname(os.path.realpath(__file__))
    contribs_path = os.path.join(this_file, '..', 'contribs')
    if structures_path:
      return [structures_path, contribs_path]
    return [contribs_path]

  def _mermaid_id(self, node):
    safe = ''.join(char if char.isalnum() else '_' for char in node)
    return f"n_{safe}"

  def _escape_mermaid_label(self, label):
    return label.replace('\\', '\\\\').replace('"', '\\"')
