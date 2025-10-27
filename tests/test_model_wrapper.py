import pytest
import os
import logging
from unittest.mock import patch, MagicMock
from structkit.model_wrapper import ModelWrapper


class TestModelWrapper:
    """Test ModelWrapper functionality including API key handling."""

    def test_init_with_existing_openai_api_key(self):
        """Test that ModelWrapper initializes correctly when OPENAI_API_KEY is already set."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test-key", "AI_MODEL": "openai:gpt-4.1"}, clear=False):
            with patch('structkit.model_wrapper.Agent') as mock_agent:
                wrapper = ModelWrapper()
                assert wrapper.model_name == "openai:gpt-4.1"
                mock_agent.assert_called_once_with(model="openai:gpt-4.1")
                # Should not set placeholder key when real key exists
                assert os.environ["OPENAI_API_KEY"] == "sk-test-key"

    def test_init_without_openai_api_key_sets_placeholder(self):
        """Test that ModelWrapper sets placeholder API key when OPENAI_API_KEY is not set."""
        # Remove OPENAI_API_KEY if it exists
        env_vars = os.environ.copy()
        if "OPENAI_API_KEY" in env_vars:
            del env_vars["OPENAI_API_KEY"]
        env_vars["AI_MODEL"] = "openai:gpt-4.1"

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('structkit.model_wrapper.Agent') as mock_agent:
                mock_logger = MagicMock()
                wrapper = ModelWrapper(logger=mock_logger)

                # Should set placeholder key
                assert os.environ["OPENAI_API_KEY"] == "sk-default-placeholder-key"
                # Should log warning
                mock_logger.warning.assert_called_with(
                    "OPENAI_API_KEY not set. Using placeholder. AI features may not work properly."
                )
                # Agent should still be created
                mock_agent.assert_called_once_with(model="openai:gpt-4.1")

    def test_init_with_non_openai_model_no_placeholder(self):
        """Test that ModelWrapper doesn't set placeholder for non-OpenAI models."""
        # Remove OPENAI_API_KEY if it exists
        env_vars = os.environ.copy()
        if "OPENAI_API_KEY" in env_vars:
            del env_vars["OPENAI_API_KEY"]
        env_vars["AI_MODEL"] = "anthropic:claude-3"

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('structkit.model_wrapper.Agent') as mock_agent:
                mock_logger = MagicMock()
                wrapper = ModelWrapper(logger=mock_logger)

                # Should not set placeholder key for non-OpenAI models
                assert "OPENAI_API_KEY" not in os.environ
                # Should not log warning
                mock_logger.warning.assert_not_called()
                # Agent should still be created
                mock_agent.assert_called_once_with(model="anthropic:claude-3")

    def test_generate_content_with_placeholder_key(self):
        """Test that generate_content handles placeholder API key gracefully."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-default-placeholder-key"}, clear=False):
            with patch('structkit.model_wrapper.Agent'):
                mock_logger = MagicMock()
                wrapper = ModelWrapper(logger=mock_logger)

                result = wrapper.generate_content("system", "user")

                assert result == "AI generation skipped: Please set OPENAI_API_KEY environment variable."
                mock_logger.warning.assert_called_with(
                    "Using placeholder API key. Set OPENAI_API_KEY environment variable for AI features to work."
                )

    def test_generate_content_with_valid_key(self):
        """Test that generate_content works normally with valid API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-valid-key"}, clear=False):
            with patch('structkit.model_wrapper.Agent') as mock_agent_class:
                mock_agent = MagicMock()
                mock_agent_class.return_value = mock_agent

                # Mock the agent run result
                mock_result = MagicMock()
                mock_result.output = "Generated content"
                mock_agent.run_sync.return_value = mock_result

                wrapper = ModelWrapper()
                result = wrapper.generate_content("system prompt", "user prompt")

                assert result == "Generated content"
                mock_agent.run_sync.assert_called_once_with("user prompt")

    def test_generate_content_dry_run(self):
        """Test that generate_content handles dry run mode."""
        with patch('structkit.model_wrapper.Agent'):
            mock_logger = MagicMock()
            wrapper = ModelWrapper(logger=mock_logger)

            result = wrapper.generate_content("system", "user", dry_run=True)

            assert result == "[DRY RUN] Generating content using AI agent"
            mock_logger.info.assert_called_with("[DRY RUN] Would generate content using AI agent.")

    def test_generate_content_api_key_error_handling(self):
        """Test that generate_content provides helpful error messages for API key issues."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-invalid-key"}, clear=False):
            with patch('structkit.model_wrapper.Agent') as mock_agent_class:
                mock_agent = MagicMock()
                mock_agent_class.return_value = mock_agent

                # Mock an API key error
                mock_agent.run_sync.side_effect = Exception("Invalid API_KEY provided")

                mock_logger = MagicMock()
                wrapper = ModelWrapper(logger=mock_logger)
                result = wrapper.generate_content("system", "user")

                assert result == "AI generation failed: Please check your OPENAI_API_KEY environment variable."
                mock_logger.error.assert_called_once()

    def test_default_model_name(self):
        """Test that default model is set correctly when AI_MODEL is not provided."""
        env_vars = os.environ.copy()
        if "AI_MODEL" in env_vars:
            del env_vars["AI_MODEL"]

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('structkit.model_wrapper.Agent'):
                wrapper = ModelWrapper()
                assert wrapper.model_name == "openai:gpt-4.1"
