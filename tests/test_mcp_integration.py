"""
Tests for MCP (Model Context Protocol) integration with FastMCP stdio transport.
"""
import asyncio
import json
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

    def test_get_structure_vars_tool_is_registered(self):
        tools = asyncio.run(self.server.app.list_tools())
        tool_names = [tool.name for tool in tools]
        self.assertIn('get_structure_vars', tool_names)
        self.assertIn('lint_structure', tool_names)

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

    def test_get_structure_vars_logic(self):
        text = self.server._get_structure_vars_logic(None)
        self.assertIn("structure_name is required", text)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'variables': [
                    {
                        'project_name': {
                            'type': 'string',
                            'default': 'MyProject',
                            'description': 'Project name'
                        }
                    },
                    {
                        'api_token': {
                            'type': 'string',
                            'help': 'API token',
                            'required': True
                        }
                    },
                ]
            }, f)
            f.flush()
            try:
                text = self.server._get_structure_vars_logic(f.name)
                self.assertIn("Variables for", text)
                self.assertIn("project_name", text)
                self.assertIn("MyProject", text)
                self.assertIn("api_token", text)
                self.assertIn("required", text)

                json_text = self.server._get_structure_vars_logic(f.name, output="json")
                data = json.loads(json_text)
                self.assertEqual(data[0]['name'], 'project_name')
                self.assertEqual(data[0]['default'], 'MyProject')
                self.assertEqual(data[1]['name'], 'api_token')
                self.assertTrue(data[1]['required'])
            finally:
                os.unlink(f.name)

    def test_get_structure_vars_logic_custom_path(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            structure_path = os.path.join(temp_dir, 'custom.yaml')
            with open(structure_path, 'w') as f:
                yaml.dump({
                    'variables': [
                        {'custom_name': {'type': 'string', 'description': 'Custom variable'}}
                    ]
                }, f)

            text = self.server._get_structure_vars_logic('custom', structures_path=temp_dir)
            self.assertIn('custom_name', text)
            self.assertIn('Custom variable', text)

    def test_get_structure_vars_compat_handler(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'variables': [{'enabled': {'type': 'boolean', 'default': True}}]}, f)
            f.flush()
            try:
                result = asyncio.run(self.server._handle_get_structure_vars({
                    'structure_name': f.name,
                    'output': 'json',
                }))
                data = json.loads(result.content[0].text)
                self.assertEqual(data[0]['name'], 'enabled')
                self.assertTrue(data[0]['default'])
            finally:
                os.unlink(f.name)


    def test_lint_structure_logic_and_compat_handler(self):
        text = self.server._lint_structure_logic([])
        self.assertIn("Provide one or more YAML files", text)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({
                'description': 'Test structure',
                'files': [
                    {'README.md': {'content': '# {{@ project_name @}}'}}
                ],
                'variables': [
                    {'project_name': {'type': 'string', 'default': 'demo'}}
                ]
            }, f)
            f.flush()
            try:
                json_text = self.server._lint_structure_logic([f.name], output='json')
                data = json.loads(json_text)
                self.assertEqual(data['summary']['errors'], 0)

                result = asyncio.run(self.server._handle_lint_structure({
                    'targets': [f.name],
                    'output': 'json',
                }))
                data = json.loads(result.content[0].text)
                self.assertEqual(data['summary']['files'], 1)
            finally:
                os.unlink(f.name)

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
