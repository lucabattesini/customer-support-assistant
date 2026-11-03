from collections.abc import Mapping
from pathlib import Path

from app.core.store_config import StoreConfig

SECTION_SEPARATOR = "\n\n"


class PromptTemplateError(ValueError):
    """Raised when a prompt template cannot be rendered."""


class PromptBuilder:
    """Loads LLM-facing text from the prompts folder.

    System prompts are split into numbered Markdown files under `agents/<agent_name>/`,
    joined in file name order and rendered with `str.format` placeholders. Tool
    descriptions live in `tools/<tool_name>.md` and are used verbatim.
    """

    def __init__(self, prompts_dir: Path) -> None:
        self._prompts_dir = prompts_dir

    def build_system_prompt(self, agent_name: str, values: Mapping[str, object]) -> str:
        """Render the system prompt of an agent.

        Args:
            agent_name: Folder name under `prompts/agents`.
            values: Values for the placeholders used in the templates.

        Returns:
            The rendered system prompt.

        Raises:
            FileNotFoundError: When the agent has no prompt files.
            PromptTemplateError: When a placeholder has no value or a template is malformed.
        """
        agent_dir = self._prompts_dir / "agents" / agent_name
        files = sorted(agent_dir.glob("*.md"))
        if not files:
            raise FileNotFoundError(f"No prompt files found in {agent_dir}")
        return SECTION_SEPARATOR.join(_render(file, values) for file in files)

    def tool_description(self, tool_name: str) -> str:
        """Return the description of a tool exactly as written in its Markdown file."""
        return (self._prompts_dir / "tools" / f"{tool_name}.md").read_text(encoding="utf-8").strip()


def store_prompt_values(config: StoreConfig) -> dict[str, str]:
    """Placeholder values taken from the store configuration."""
    return {
        "store_name": config.store.name,
        "store_tagline": config.store.tagline,
        "store_city": config.store.city,
    }


def _render(file: Path, values: Mapping[str, object]) -> str:
    template = file.read_text(encoding="utf-8").strip()
    try:
        return template.format_map(values)
    except KeyError as error:
        raise PromptTemplateError(
            f"Missing value for placeholder {error} in {file.name}"
        ) from error
    except (IndexError, ValueError) as error:
        raise PromptTemplateError(f"Malformed template {file.name}: {error}") from error
