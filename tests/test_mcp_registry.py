"""Checks that keep the official MCP Registry listing metadata consistent."""
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVER_JSON = ROOT / "server.json"
PYPROJECT = ROOT / "pyproject.toml"
README = ROOT / "README.md"
SERVER_NAME = "io.github.httpdss/structkit"
OWNERSHIP_MARKER = f"mcp-name: {SERVER_NAME}"


class TestMCPRegistryMetadata(unittest.TestCase):
    def setUp(self):
        self.server = json.loads(SERVER_JSON.read_text())
        pyproject_text = PYPROJECT.read_text()
        match = re.search(r'(?m)^version\s*=\s*"([^"]+)"', pyproject_text)
        if match is None:
            self.fail("pyproject.toml version field was not found")
        self.package_version = match.group(1)
        self.readme = README.read_text()

    def test_server_json_identity(self):
        self.assertEqual(self.server["name"], SERVER_NAME)
        self.assertEqual(self.server["title"], "StructKit")
        self.assertGreaterEqual(len(self.server["description"]), 1)
        self.assertLessEqual(len(self.server["description"]), 100)
        self.assertEqual(self.server["repository"]["url"], "https://github.com/httpdss/structkit")
        self.assertEqual(self.server["repository"]["source"], "github")
        self.assertEqual(self.server["repository"]["id"], "827469347")

    def test_versions_match_pyproject(self):
        self.assertEqual(self.server["version"], self.package_version)
        self.assertEqual(self.server["packages"][0]["version"], self.package_version)

    def test_pypi_package_launches_mcp_server(self):
        package = self.server["packages"][0]
        self.assertEqual(package["registryType"], "pypi")
        self.assertEqual(package["identifier"], "structkit")
        self.assertEqual(package["runtimeHint"], "uvx")
        self.assertEqual(package["transport"]["type"], "stdio")
        arguments = [
            (item.get("type"), item.get("value"))
            for item in package["packageArguments"]
        ]
        self.assertEqual(arguments, [("positional", "mcp"), ("positional", "--server")])

    def test_readme_ownership_marker_is_hidden(self):
        self.assertIn(f"<!-- {OWNERSHIP_MARKER} -->", self.readme)
        self.assertIn(OWNERSHIP_MARKER, self.readme)


if __name__ == "__main__":
    unittest.main()
