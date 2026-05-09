import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

from structkit.commands import Command
from structkit.completers import structures_completer


class GraphCommand(Command):
    """Visualize dependency relationships between StructKit structures."""

    def __init__(self, parser):
      super().__init__(parser)
      parser.description = "Visualize structure dependencies from folders[].struct references"
      structure_arg = parser.add_argument('structure_definition', nargs='?', type=str, help='Structure name or local YAML file to graph')
      structure_arg.completer = structures_completer
      parser.add_argument(
        '-s',
        '--structures-path',
        type=str,
        help='Path to structure definitions (env: STRUCTKIT_STRUCTURES_PATH)',
        default=os.getenv('STRUCTKIT_STRUCTURES_PATH', None)
      )
      parser.add_argument('--all', action='store_true', help='Graph all available built-in and custom structures')
      parser.add_argument(
        '--format',
        choices=['text', 'json', 'mermaid'],
        default='text',
        help='Output format (default: text)'
      )
      parser.set_defaults(func=self.execute)

    def execute(self, args):
      if not args.all and not args.structure_definition:
        self.parser.error('provide a structure name, a YAML file, or --all')
      if args.all and args.structure_definition:
        self.parser.error('provide either a structure name/YAML file or --all, not both')

      graph = self.build_graph(
        structure_definition=args.structure_definition,
        structures_path=args.structures_path,
        all_structures=args.all,
      )
      print(self.format_graph(graph, args.format))

    def build_graph(
        self,
        structure_definition: Optional[str] = None,
        structures_path: Optional[str] = None,
        all_structures: bool = False,
    ) -> Dict[str, Any]:
      roots = self._list_available_structures(structures_path) if all_structures else [structure_definition]
      graph = {
        'roots': roots,
        'nodes': [],
        'edges': [],
        'missing': [],
        'cycles': [],
      }
      state = {
        'node_names': set(),
        'edge_keys': set(),
        'missing_keys': set(),
        'cycle_keys': set(),
      }

      for root in roots:
        if root:
          self._walk(root, structures_path, graph, state, [])

      return graph

    def format_graph(self, graph: Dict[str, Any], output_format: str = 'text') -> str:
      if output_format == 'json':
        return json.dumps(graph, indent=2)
      if output_format == 'mermaid':
        return self._format_mermaid(graph)
      return self._format_text(graph)

    def _walk(
        self,
        structure_definition: str,
        structures_path: Optional[str],
        graph: Dict[str, Any],
        state: Dict[str, Set[Any]],
        stack: List[str],
    ):
      node_name = self._display_name(structure_definition)
      config, source = self._load_yaml_config(structure_definition, structures_path)

      if node_name not in state['node_names']:
        graph['nodes'].append({
          'name': node_name,
          'source': source,
          'missing': config is None,
        })
        state['node_names'].add(node_name)

      if config is None:
        return
      if not isinstance(config, dict):
        return

      if node_name in stack:
        self._add_cycle(stack + [node_name], graph, state)
        return

      next_stack = stack + [node_name]
      for dependency, folder in self._iter_dependencies(config):
        dep_name = self._display_name(dependency)
        edge_key = (node_name, dep_name, folder)
        if edge_key not in state['edge_keys']:
          graph['edges'].append({'from': node_name, 'to': dep_name, 'folder': folder})
          state['edge_keys'].add(edge_key)

        if dep_name in next_stack:
          self._add_cycle(next_stack + [dep_name], graph, state)
          continue

        dep_config, dep_source = self._load_yaml_config(dependency, structures_path)
        if dep_config is None:
          if dep_name not in state['node_names']:
            graph['nodes'].append({'name': dep_name, 'source': dep_source, 'missing': True})
            state['node_names'].add(dep_name)
          missing_key = (node_name, dep_name)
          if missing_key not in state['missing_keys']:
            graph['missing'].append({'from': node_name, 'to': dep_name, 'folder': folder, 'source': dep_source})
            state['missing_keys'].add(missing_key)
          continue

        self._walk(dependency, structures_path, graph, state, next_stack)

    def _add_cycle(self, cycle: List[str], graph: Dict[str, Any], state: Dict[str, Set[Any]]):
      key = tuple(cycle)
      if key not in state['cycle_keys']:
        graph['cycles'].append(cycle)
        state['cycle_keys'].add(key)

    def _iter_dependencies(self, config: Dict[str, Any]) -> List[Tuple[str, str]]:
      dependencies = []
      for item in config.get('folders', []) or []:
        if not isinstance(item, dict):
          continue
        for folder, content in item.items():
          if not isinstance(content, dict):
            continue
          structs = content.get('struct') or content.get('structkit')
          if isinstance(structs, str):
            structs = [structs]
          if not isinstance(structs, list):
            continue
          for nested_struct in structs:
            if isinstance(nested_struct, str) and nested_struct:
              dependencies.append((nested_struct, str(folder)))
      return dependencies

    def _load_yaml_config(self, structure_definition: str, structures_path: Optional[str]):
      file_path = self._resolve_structure_path(structure_definition, structures_path)
      if not file_path or not os.path.exists(file_path):
        return None, file_path
      try:
        with open(file_path, 'r') as f:
          return yaml.safe_load(f) or {}, file_path
      except (OSError, yaml.YAMLError) as exc:
        self.logger.error(f"❗ Failed to load {file_path}: {exc}")
        return None, file_path

    def _resolve_structure_path(self, structure_definition: str, structures_path: Optional[str]) -> Optional[str]:
      if structure_definition.startswith('file://'):
        return structure_definition[7:]
      if structure_definition.endswith(('.yaml', '.yml')):
        return structure_definition

      this_file = os.path.dirname(os.path.realpath(__file__))
      contribs_path = os.path.join(this_file, '..', 'contribs')
      candidates = []
      if structures_path:
        candidates.append(os.path.join(structures_path, f'{structure_definition}.yaml'))
        candidates.append(os.path.join(structures_path, f'{structure_definition}.yml'))
      candidates.append(os.path.join(contribs_path, f'{structure_definition}.yaml'))
      candidates.append(os.path.join(contribs_path, f'{structure_definition}.yml'))
      for candidate in candidates:
        if os.path.exists(candidate):
          return candidate
      return candidates[0] if candidates else None

    def _list_available_structures(self, structures_path: Optional[str]) -> List[str]:
      this_file = os.path.dirname(os.path.realpath(__file__))
      contribs_path = os.path.join(this_file, '..', 'contribs')
      paths = []
      if structures_path:
        paths.append(structures_path)
      paths.append(contribs_path)

      names = set()
      for path in paths:
        if not path or not os.path.exists(path):
          continue
        for root, _, files in os.walk(path):
          for file_name in files:
            if not file_name.endswith(('.yaml', '.yml')):
              continue
            rel = os.path.relpath(os.path.join(root, file_name), path)
            rel = os.path.splitext(rel)[0]
            names.add(rel)
      return sorted(names)

    def _display_name(self, structure_definition: str) -> str:
      if structure_definition.startswith('file://'):
        return structure_definition[7:]
      return structure_definition

    def _format_text(self, graph: Dict[str, Any]) -> str:
      children: Dict[str, List[Dict[str, str]]] = {}
      for edge in graph['edges']:
        children.setdefault(edge['from'], []).append(edge)

      lines = ['Dependency graph:']
      for root in graph['roots']:
        if not root:
          continue
        root_name = self._display_name(root)
        lines.extend(self._format_text_node(root_name, children, set(), ''))

      if graph['missing']:
        lines.append('')
        lines.append('Missing references:')
        for missing in graph['missing']:
          lines.append(f"  - {missing['from']} -> {missing['to']} (folder: {missing['folder']})")

      if graph['cycles']:
        lines.append('')
        lines.append('Cycles:')
        for cycle in graph['cycles']:
          lines.append(f"  - {' -> '.join(cycle)}")

      if not graph['missing'] and not graph['cycles']:
        lines.append('')
        lines.append('No missing references or cycles detected.')

      return '\n'.join(lines)

    def _format_text_node(self, node: str, children: Dict[str, List[Dict[str, str]]], stack: Set[str], prefix: str) -> List[str]:
      lines = [node] if not prefix else [f'{prefix}{node}']
      if node in stack:
        lines[-1] += ' (cycle)'
        return lines

      next_stack = set(stack)
      next_stack.add(node)
      edges = children.get(node, [])
      for index, edge in enumerate(edges):
        is_last = index == len(edges) - 1
        lines.extend(self._format_text_child(edge['to'], children, next_stack, '', is_last))
      return lines

    def _format_text_child(
        self,
        node: str,
        children: Dict[str, List[Dict[str, str]]],
        stack: Set[str],
        prefix: str,
        is_last: bool,
    ) -> List[str]:
      connector = '└── ' if is_last else '├── '
      line = f'{prefix}{connector}{node}'
      if node in stack:
        return [line + ' (cycle)']

      next_stack = set(stack)
      next_stack.add(node)
      edges = children.get(node, [])
      lines = [line]
      child_prefix = prefix + ('    ' if is_last else '│   ')
      for index, edge in enumerate(edges):
        lines.extend(self._format_text_child(edge['to'], children, next_stack, child_prefix, index == len(edges) - 1))
      return lines

    def _format_mermaid(self, graph: Dict[str, Any]) -> str:
      node_ids = {node['name']: f'n{index}' for index, node in enumerate(graph['nodes'])}
      lines = ['graph TD']
      if not graph['nodes']:
        return '\n'.join(lines)

      for node in graph['nodes']:
        label = self._escape_mermaid_label(node['name'])
        lines.append(f'  {node_ids[node["name"]]}["{label}"]')

      for edge in graph['edges']:
        lines.append(f'  {node_ids[edge["from"]]} --> {node_ids[edge["to"]]}')

      missing_nodes = [node_ids[node['name']] for node in graph['nodes'] if node.get('missing')]
      if missing_nodes:
        lines.append('  classDef missing fill:#ffe6e6,stroke:#cc0000,color:#660000')
        lines.append(f'  class {",".join(missing_nodes)} missing')
      return '\n'.join(lines)

    def _escape_mermaid_label(self, value: str) -> str:
      return re.sub(r'"', r'\\"', value)
