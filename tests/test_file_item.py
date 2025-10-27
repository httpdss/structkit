import pytest
from unittest.mock import patch, MagicMock
from structkit.file_item import FileItem

@pytest.fixture
def file_item():
    properties = {
        "name": "test.txt",
        "content": "file content",
        "config_variables": [],
        "input_store": "/tmp/input.json"
    }
    return FileItem(properties)

def test_apply_template_variables(file_item):
    template_vars = {"var1": "value1"}
    file_item.apply_template_variables(template_vars)
    assert file_item.content == "file content"

def test_fetch_content(file_item):
    with patch('structkit.content_fetcher.ContentFetcher.fetch_content') as mock_fetch:
        mock_fetch.return_value = "fetched content"
        file_item.fetch_content()
        assert file_item.content == "file content"


def test_fetch_content_renders_template(monkeypatch):
    properties = {
        "name": "test.txt",
        "file": "/fake/path.txt",
        "config_variables": [],
        "input_store": "/tmp/input.json"
    }
    file_item = FileItem(properties)

    # Mock fetch_content to return a template string
    monkeypatch.setattr(
        file_item.content_fetcher,
        "fetch_content",
        lambda location: "Hello, {{@ name @}}!"
    )
    # Mock template renderer methods
    rendered = {}

    def fake_prompt_for_missing_vars(content, vars):
        return {"name": "World"}

    def fake_render_template(content, vars):
        rendered["content"] = content
        rendered["vars"] = vars
        return "Hello, World!"
    file_item.template_renderer.prompt_for_missing_vars = fake_prompt_for_missing_vars
    file_item.template_renderer.render_template = fake_render_template

    file_item.fetch_content()
    assert file_item.content == "Hello, World!"
    assert rendered["content"] == "Hello, {{@ name @}}!"
    assert rendered["vars"]["name"] == "World"
