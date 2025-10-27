import json
import os
import re
from uuid import UUID
from datetime import datetime

import pytest

from structkit.template_renderer import TemplateRenderer


@pytest.fixture
def renderer(tmp_path):
    # minimal renderer with non_interactive to avoid prompts
    return TemplateRenderer(config_variables=[], input_store=str(tmp_path / "inputs.json"), non_interactive=True)


def test_uuid_global(renderer):
    tmpl = "ID: {{@ uuid() @}}"
    out = renderer.render_template(tmpl, {})
    # Extract UUID part and validate format
    uid = out.split("ID: ")[-1].strip()
    # Will raise if invalid
    UUID(uid)


def test_now_global(renderer):
    tmpl = "TS: {{@ now() @}}"
    out = renderer.render_template(tmpl, {})
    ts = out.split("TS: ")[-1].strip()
    # Should be ISO 8601 parseable
    parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    assert isinstance(parsed, datetime)


def test_env_global(monkeypatch, renderer):
    monkeypatch.setenv("FOO_BAR", "baz")
    tmpl = "{{@ env('FOO_BAR', 'default') @}}|{{@ env('MISSING_VAR', 'fallback') @}}"
    out = renderer.render_template(tmpl, {})
    left, right = out.split("|")
    assert left == "baz"
    assert right == "fallback"


def test_read_file_global(tmp_path, renderer):
    p = tmp_path / "hello.txt"
    p.write_text("hello world", encoding="utf-8")
    tmpl = "{{@ read_file('" + str(p) + "') @}}|{{@ read_file('nonexistent') @}}"
    out = renderer.render_template(tmpl, {})
    left, right = out.split("|")
    assert left == "hello world"
    assert right == ""


def test_yaml_filters(renderer):
    # Render a dict into YAML and parse back
    tmpl = "{%@ set y = data | to_yaml @%}{%@ set back = y | from_yaml @%}{{@ back.name @}}:{{@ back.value @}}"
    out = renderer.render_template(tmpl, {"data": {"name": "item", "value": 42}})
    assert out == "item:42"


def test_json_filters(renderer):
    tmpl = "{%@ set j = data | to_json @%}{%@ set back = j | from_json @%}{{@ back.kind @}}:{{@ back.count @}}"
    out = renderer.render_template(tmpl, {"data": {"kind": "k", "count": 7}})
    assert out == "k:7"
