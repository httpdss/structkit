import pytest
from unittest.mock import patch, MagicMock
from structkit.template_renderer import TemplateRenderer

@pytest.fixture
def renderer():
    config_variables = [
        {"var1": {"type": "string", "default": "default1"}},
        {"var2": {"type": "string", "default": "default2"}}
    ]
    input_store = "/tmp/input.json"
    non_interactive = False
    return TemplateRenderer(config_variables, input_store, non_interactive)

def test_render_template(renderer):
    content = "Hello, {{@ var1 @}}!"
    vars = {"var1": "World"}
    rendered_content = renderer.render_template(content, vars)
    assert rendered_content == "Hello, World!"

def test_prompt_for_missing_vars(renderer):
    content = "Hello, {{@ var1 @}} and {{@ var2 @}}!"
    vars = {"var1": "World"}
    with patch('builtins.input', side_effect=["Universe"]):
        missing_vars = renderer.prompt_for_missing_vars(content, vars)
        assert missing_vars["var2"] == "Universe"


def test_defaults_from_env_renderer(monkeypatch):
    config_variables = [
        {"TOKEN": {"type": "string", "env": "MY_TOKEN"}},
    ]
    input_store = "/tmp/input.json"
    non_interactive = True
    monkeypatch.setenv("MY_TOKEN", "abc123")
    r = TemplateRenderer(config_variables, input_store, non_interactive)
    defaults = r.get_defaults_from_config()
    assert defaults["TOKEN"] == "abc123"


def test_type_coercion_and_validation(monkeypatch):
    config_variables = [
        {"IS_ENABLED": {"type": "boolean", "required": True}},
        {"RETRY": {"type": "integer", "min": 1, "max": 5}},
        {"ENV": {"type": "string", "enum": ["dev", "prod"]}},
    ]
    input_store = "/tmp/input.json"
    non_interactive = False
    r = TemplateRenderer(config_variables, input_store, non_interactive)
    content = "{{@ IS_ENABLED @}} {{@ RETRY @}} {{@ ENV @}}"

    # Provide inputs mapped by variable name (order-agnostic)
    def fake_input(prompt):
        if 'IS_ENABLED' in prompt:
            return 'yes'
        if 'RETRY' in prompt:
            return '3'
        if 'ENV' in prompt:
            return 'prod'
        return ''
    with patch('builtins.input', side_effect=fake_input):
        vars = {}
        out = r.prompt_for_missing_vars(content, vars)
        assert out["IS_ENABLED"] is True
        assert out["RETRY"] == 3
        assert out["ENV"] == "prod"

    # Enum violation should raise
    r = TemplateRenderer(config_variables, input_store, non_interactive)
    with patch('builtins.input', side_effect=["true", "2", "staging"]):
        with pytest.raises(ValueError):
            r.prompt_for_missing_vars(content, {})

def test_get_defaults_from_config(renderer):
    defaults = renderer.get_defaults_from_config()
    assert defaults == {"var1": "default1", "var2": "default2"}


def test_render_template_with_mappings():
    config_variables = []
    input_store = "/tmp/input.json"
    non_interactive = True
    mappings = {
        "aws_account_ids": {
            "myenv-non-prod": "123456789",
            "myenv-prod": "987654321"
        }
    }
    renderer = TemplateRenderer(
        config_variables, input_store, non_interactive, mappings=mappings)
    content = "Account: {{@ mappings.aws_account_ids['myenv-prod'] @}}"
    rendered_content = renderer.render_template(content, {})
    assert rendered_content == "Account: 987654321"

    # Also test dot notation
    content_dot = "Account: {{@ mappings.aws_account_ids.myenv_non_prod @}}"
    # Jinja2 does not allow dash in dot notation, so we use underscore for this test
    mappings_dot = {
        "aws_account_ids": {
            "myenv_non_prod": "123456789",
            "myenv_prod": "987654321"
        }
    }
    renderer_dot = TemplateRenderer(
        config_variables, input_store, non_interactive, mappings=mappings_dot)
    rendered_content_dot = renderer_dot.render_template(content_dot, {})
    assert rendered_content_dot == "Account: 123456789"


def test_prompt_with_description_display():
    """Test that variable descriptions are displayed in interactive prompts with Option 4 formatting"""
    config_variables = [
        {"project_name": {
            "type": "string",
            "description": "The name of your project",
            "default": "MyProject"
        }},
        {"environment": {
            "type": "string",
            "description": "Target deployment environment",
            "enum": ["dev", "staging", "prod"],
            "default": "dev"
        }},
        {"old_style_help": {
            "type": "string",
            "help": "This uses the old 'help' field",
            "default": "test"
        }},
        {"no_description": {
            "type": "string",
            "default": "test"
        }}
    ]
    input_store = "/tmp/input.json"
    non_interactive = False
    renderer = TemplateRenderer(config_variables, input_store, non_interactive)

    # Test each variable type separately to ensure proper input handling

    # Test 1: Regular variable with description (should show icon + description format)
    content1 = "{{@ project_name @}}"
    vars1 = {}
    with patch('builtins.input', return_value="TestProject") as mock_input, \
         patch('builtins.print') as mock_print:
        result_vars1 = renderer.prompt_for_missing_vars(content1, vars1)
        assert result_vars1["project_name"] == "TestProject"

        # Check that the new format was printed (icon + bold var: description)
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("🚀 \033[1mproject_name\033[0m: The name of your project" in call for call in print_calls)

    # Test 2: Enum variable with description (should show icon + description + options)
    content2 = "{{@ environment @}}"
    vars2 = {}
    with patch('builtins.input', return_value="prod") as mock_input, \
         patch('builtins.print') as mock_print:
        result_vars2 = renderer.prompt_for_missing_vars(content2, vars2)
        assert result_vars2["environment"] == "prod"

        # Check that description and options were printed in new format with bold
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("🌍 \033[1menvironment\033[0m: Target deployment environment" in call for call in print_calls)
        assert any("Options: (1) dev, (2) staging, (3) prod" in call for call in print_calls)

    # Test 3: Variable with 'help' field (backward compatibility)
    content3 = "{{@ old_style_help @}}"
    vars3 = {}
    with patch('builtins.input', return_value="help_test") as mock_input, \
         patch('builtins.print') as mock_print:
        result_vars3 = renderer.prompt_for_missing_vars(content3, vars3)
        assert result_vars3["old_style_help"] == "help_test"

        # Check that help was printed in new format with bold
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        assert any("🔧 \033[1mold_style_help\033[0m: This uses the old 'help' field" in call for call in print_calls)

    # Test 4: Variable without description (should use compact format with icon)
    content4 = "{{@ no_description @}}"
    vars4 = {}
    with patch('builtins.input', return_value="no_desc_test") as mock_input, \
         patch('builtins.print') as mock_print:
        result_vars4 = renderer.prompt_for_missing_vars(content4, vars4)
        assert result_vars4["no_description"] == "no_desc_test"

        # Check that no description line was printed (should use inline format)
        print_calls = [call.args[0] for call in mock_print.call_args_list]
        # Should not contain the two-line format with description
        assert not any(": " in call and "no_description" in call for call in print_calls)

def test_variable_icon_selection():
    """Test that appropriate icons are selected for different variable types"""
    config_variables = []
    input_store = "/tmp/input.json"
    non_interactive = True
    renderer = TemplateRenderer(config_variables, input_store, non_interactive)

    # Test icon selection logic
    assert renderer._get_variable_icon("project_name", "string") == "🚀"
    assert renderer._get_variable_icon("environment", "string") == "🌍"
    assert renderer._get_variable_icon("port", "integer") == "🔌"
    assert renderer._get_variable_icon("enable_logging", "boolean") == "⚡"
    assert renderer._get_variable_icon("api_token", "string") == "🔐"
    assert renderer._get_variable_icon("database_url", "string") == "🗄️"
    assert renderer._get_variable_icon("version", "string") == "🏷️"
    assert renderer._get_variable_icon("config_path", "string") == "📁"
    assert renderer._get_variable_icon("random_var", "string") == "🔧"
