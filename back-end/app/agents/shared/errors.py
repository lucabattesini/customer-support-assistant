class AgentError(Exception):
    """Base error for failures while producing an agent reply."""


class LLMNotConfiguredError(AgentError):
    """The LLM provider credentials or model are missing."""


class LLMUnavailableError(AgentError):
    """The LLM provider failed, timed out or rejected the request."""


class AgentStepLimitError(AgentError):
    """The agent reached the maximum number of model calls for a single message."""
