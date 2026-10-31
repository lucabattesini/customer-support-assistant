import pytest

from app.agents.shared.prompt_builder import PromptBuilder, PromptTemplateError, store_prompt_values
from app.core.settings import BASE_DIR

PROMPTS_DIR = BASE_DIR / "prompts"
TOOL_NAMES = [
    "search_products",
    "get_product_details",
    "get_order_status",
    "check_return_eligibility",
    "get_policy",
    "get_current_datetime",
    "handoff_to_human",
]


@pytest.fixture
def builder():
    return PromptBuilder(PROMPTS_DIR)


def test_real_system_prompt_renders_with_store_values(builder, store_config):
    prompt = builder.build_system_prompt("customer_support", store_prompt_values(store_config))

    assert store_config.store.name in prompt
    assert "{" not in prompt and "}" not in prompt


def test_system_prompt_sections_follow_file_order(builder, store_config):
    prompt = builder.build_system_prompt("customer_support", store_prompt_values(store_config))
    headings = [line for line in prompt.splitlines() if line.startswith("# ")]

    assert headings == ["# Identity", "# Behavior", "# Rules", "# Scope", "# Output format"]


@pytest.mark.parametrize("tool_name", TOOL_NAMES)
def test_every_tool_has_a_description(builder, tool_name):
    assert len(builder.tool_description(tool_name)) > 50


def test_missing_placeholder_value_fails_clearly(tmp_path):
    agent_dir = tmp_path / "agents" / "demo"
    agent_dir.mkdir(parents=True)
    (agent_dir / "01_intro.md").write_text("Hello {store_name}", encoding="utf-8")

    with pytest.raises(PromptTemplateError, match="store_name"):
        PromptBuilder(tmp_path).build_system_prompt("demo", {})


def test_literal_braces_must_be_escaped(tmp_path):
    agent_dir = tmp_path / "agents" / "demo"
    agent_dir.mkdir(parents=True)
    (agent_dir / "01_intro.md").write_text('Return {{"ok": true}} for {name}', encoding="utf-8")

    prompt = PromptBuilder(tmp_path).build_system_prompt("demo", {"name": "x"})

    assert prompt == 'Return {"ok": true} for x'


def test_files_are_joined_in_name_order_with_utf8(tmp_path):
    agent_dir = tmp_path / "agents" / "demo"
    agent_dir.mkdir(parents=True)
    (agent_dir / "02_second.md").write_text("Música", encoding="utf-8")
    (agent_dir / "01_first.md").write_text("Primeira", encoding="utf-8")

    assert PromptBuilder(tmp_path).build_system_prompt("demo", {}) == "Primeira\n\nMúsica"


def test_unknown_agent_raises(builder):
    with pytest.raises(FileNotFoundError):
        builder.build_system_prompt("unknown_agent", {})
