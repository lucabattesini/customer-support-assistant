from langgraph.checkpoint.memory import InMemorySaver


def build_checkpointer() -> InMemorySaver:
    """In-memory conversation state keyed by thread id.

    State lives only while the process runs and is not shared between processes.
    """
    return InMemorySaver()
