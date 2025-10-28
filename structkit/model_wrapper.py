import os
import logging
from dotenv import load_dotenv
from pydantic_ai import Agent

load_dotenv()


class ModelWrapper:
  """
  Wraps model logic using pydantic-ai Agent, allowing use of multiple LLM providers.
  """
  def __init__(self, logger=None):
    self.logger = logger or logging.getLogger(__name__)
    self.model_name = os.getenv("AI_MODEL") or "openai:gpt-4.1"

    # Set default API key if not provided to prevent startup crashes
    if self.model_name.startswith("openai:") and not os.getenv("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = "sk-default-placeholder-key"
        self.logger.warning("OPENAI_API_KEY not set. Using placeholder. AI features may not work properly.")

    self.agent = Agent(model=self.model_name)
    self.logger.debug(f"Configured Agent with model: {self.model_name}")

  def generate_content(self, system_prompt, user_prompt, dry_run=False):
    if not self.agent:
      self.logger.warning("No agent configured. Skipping content generation.")
      return "No agent configured. Skipping content generation."
    if dry_run:
      self.logger.info("[DRY RUN] Would generate content using AI agent.")
      return "[DRY RUN] Generating content using AI agent"

    # Check if using placeholder API key
    if os.getenv("OPENAI_API_KEY") == "sk-default-placeholder-key":
      self.logger.warning("Using placeholder API key. Set OPENAI_API_KEY environment variable for AI features to work.")
      return "AI generation skipped: Please set OPENAI_API_KEY environment variable."

    prompt = f"{user_prompt}"
    try:
      self.agent.system_prompt = system_prompt
      result = self.agent.run_sync(prompt)
      return result.output
    except Exception as e:
      self.logger.error(f"AI agent generation failed: {e}")
      # Provide more helpful error message for API key issues
      if "api_key" in str(e).lower() or "unauthorized" in str(e).lower():
        return "AI generation failed: Please check your OPENAI_API_KEY environment variable."
      return f"AI agent generation failed: {e}"
