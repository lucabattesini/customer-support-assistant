from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.agents.shared.history import trim_history


def tool_turn(index):
    call_id = f"call_{index}"
    return [
        HumanMessage(content=f"question {index}"),
        AIMessage(content="", tool_calls=[{"name": "get_policy", "args": {}, "id": call_id}]),
        ToolMessage(content="{}", tool_call_id=call_id),
        AIMessage(content=f"answer {index}"),
    ]


def plain_turn(index):
    return [HumanMessage(content=f"question {index}"), AIMessage(content=f"answer {index}")]


def contents(messages):
    return [message.content for message in messages]


def test_keeps_only_the_last_turns():
    messages = [message for index in range(1, 9) for message in plain_turn(index)]

    trimmed = trim_history(messages, max_turns=3)

    assert contents(trimmed) == [
        "question 6",
        "answer 6",
        "question 7",
        "answer 7",
        "question 8",
        "answer 8",
    ]


def test_previous_turns_drop_tool_calls_and_results():
    messages = tool_turn(1) + tool_turn(2) + [HumanMessage(content="question 3")]

    trimmed = trim_history(messages, max_turns=6)

    assert contents(trimmed) == ["question 1", "answer 1", "question 2", "answer 2", "question 3"]
    assert not any(isinstance(message, ToolMessage) for message in trimmed)


def test_current_turn_keeps_tool_calls_paired_with_results():
    current = tool_turn(3)[:3]
    messages = tool_turn(1) + current

    trimmed = trim_history(messages, max_turns=6)

    assert trimmed[-3:] == current


def test_trimmed_history_always_starts_with_customer_message():
    messages = tool_turn(1) + tool_turn(2) + tool_turn(3)

    trimmed = trim_history(messages, max_turns=2)

    assert isinstance(trimmed[0], HumanMessage)
    assert trimmed[0].content == "question 2"


def test_messages_before_first_customer_message_are_dropped():
    messages = [AIMessage(content="orphan"), *plain_turn(1)]

    assert contents(trim_history(messages, max_turns=6)) == ["question 1", "answer 1"]


def test_empty_history():
    assert trim_history([], max_turns=6) == []
