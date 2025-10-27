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
