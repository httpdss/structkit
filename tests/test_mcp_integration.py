"""
Tests for MCP (Model Context Protocol) integration with FastMCP stdio transport.
"""
import os
import tempfile
import unittest
import yaml

from structkit.mcp_server import StructMCPServer


class TestMCPIntegration(unittest.TestCase):
    """Test cases for FastMCP-based MCP integration."""

    def setUp(self):
        self.server = StructMCPServer()

    def test_server_initialization(self):
        self.assertIsNotNone(self.server)
        self.assertTrue(hasattr(self.server, 'app'))

    def test_list_structures_logic(self):
        text = self.server._list_structures_logic()
        self.assertIsInstance(text, str)
        self.assertIn("Available structures", text)

    def test_get_structure_info_logic(self):
        # Missing structure name
        text = self.server._get_structure_info_logic(None)
        self.assertIn("structure_name is required", text)
        # Non-existent
        text = self.server._get_structure_info_logic("non_existent_structure")
        self.assertIn("Structure not found", text)

    def test_generate_structure_logic(self):
        # Missing required handled by logic caller; here provide invalid but structured args
        with tempfile.TemporaryDirectory() as temp_dir:
            # This may error silently if structure doesn't exist; ensure it returns a string
            text = self.server._generate_structure_logic(
                structure_definition="non_existent",
                base_path=temp_dir,
                output="console",
            )
            self.assertIsInstance(text, str)


    def test_source_management_logic(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'sources.json')
            source_dir = os.path.join(temp_dir, 'source')
            os.makedirs(source_dir)

            from unittest.mock import patch
            with patch.dict(os.environ, {'STRUCTKIT_SOURCES_CONFIG': config_path}):
                self.assertEqual(self.server._list_sources_logic(), 'No sources configured')

                added = self.server._add_source_logic('company', source_dir)
                self.assertIn("Added source 'company'", added)

                listed = self.server._list_sources_logic()
                self.assertIn('company', listed)
                self.assertIn(source_dir, listed)

                shown = self.server._show_source_logic('company')
                self.assertIn(source_dir, shown)

                validated = self.server._validate_source_logic('company')
                self.assertIn("Source 'company' is valid", validated)

                removed = self.server._remove_source_logic('company')
                self.assertIn("Removed source 'company'", removed)

    def test_source_management_logic_errors(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'sources.json')

            from unittest.mock import patch
            with patch.dict(os.environ, {'STRUCTKIT_SOURCES_CONFIG': config_path}):
                self.assertIn('name is required', self.server._add_source_logic(None, temp_dir))
                self.assertIn('path_or_url is required', self.server._add_source_logic('company', None))
                self.assertIn('Only local filesystem', self.server._add_source_logic('remote', 'https://example.com/templates.git'))
                self.assertIn('Unknown source', self.server._show_source_logic('missing'))

    def test_structure_logic_accepts_named_source(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = os.path.join(temp_dir, 'sources.json')
            source_dir = os.path.join(temp_dir, 'source')
            os.makedirs(os.path.join(source_dir, 'project'))
            structure_file = os.path.join(source_dir, 'project', 'python.yaml')
            with open(structure_file, 'w') as f:
                yaml.dump({'description': 'Custom Python structure', 'files': []}, f)

            from unittest.mock import patch
            with patch.dict(os.environ, {'STRUCTKIT_SOURCES_CONFIG': config_path}):
                self.server._add_source_logic('company', source_dir)

                listed = self.server._list_structures_logic(source='company')
                self.assertIn('+ project/python', listed)

                explicit = self.server._get_structure_info_logic('project/python', source='company')
                self.assertIn('Custom Python structure', explicit)

                prefixed = self.server._get_structure_info_logic('company/project/python')
                self.assertIn('Custom Python structure', prefixed)

    def test_validate_structure_logic(self):
        # Missing yaml_file
        text = self.server._validate_structure_logic(None)
        self.assertIn("yaml_file is required", text)
        # Valid YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'files': [
                    {'test.txt': {'content': 'Hello World'}}
                ],
                'description': 'Test structure'
            }, f)
            f.flush()
            try:
                res = self.server._validate_structure_logic(f.name)
                self.assertIsInstance(res, str)
            finally:
                os.unlink(f.name)


class TestMCPCommands(unittest.TestCase):
    """Test MCP command line integration."""

    def test_mcp_command_import(self):
        from structkit.commands.mcp import MCPCommand
        self.assertIsNotNone(MCPCommand)

    def test_list_command_mcp_option(self):
        from structkit.commands.list import ListCommand
        import argparse

        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()
        list_parser = subparser.add_parser('list')

        list_cmd = ListCommand(list_parser)

        args = parser.parse_args(['list', '--mcp'])
        self.assertTrue(hasattr(args, 'mcp'))

    def test_info_command_mcp_option(self):
        from structkit.commands.info import InfoCommand
        import argparse

        parser = argparse.ArgumentParser()
        subparser = parser.add_subparsers()
        info_parser = subparser.add_parser('info')

        info_cmd = InfoCommand(info_parser)

        args = parser.parse_args(['info', 'test_structure', '--mcp'])
        self.assertTrue(hasattr(args, 'mcp'))
        self.assertEqual(args.structure_definition, 'test_structure')


if __name__ == '__main__':
    unittest.main()
