import re

import pytest
from fastapi.testclient import TestClient

from app.agents.customer_support.agent import CustomerSupportAgent
from app.agents.shared.errors import AgentStepLimitError, LLMUnavailableError
from app.api.dependencies import get_chat_controller
from app.controllers.chat_controller import ChatController
from app.core.settings import Settings
from app.main import create_app

MAX_MESSAGE_LENGTH = 50


class FakeAgent:
    def __init__(self, error=None):
        self.calls = []
        self._error = error

    def reply(self, thread_id, message):
        self.calls.append((thread_id, message))
        if self._error:
            raise self._error
        return f"echo: {message}"


def build_settings(**overrides):
    return Settings(_env_file=None, database_url="sqlite://", **overrides)


@pytest.fixture
def make_client():
    clients = []

    def build(agent=None, **settings_overrides):
        app = create_app(build_settings(**settings_overrides))
        if agent is not None:
            controller = ChatController(agent, MAX_MESSAGE_LENGTH)
            app.dependency_overrides[get_chat_controller] = lambda: controller
        client = TestClient(app)
        client.__enter__()
        clients.append(client)
        return client

    yield build
    for client in clients:
        client.__exit__(None, None, None)


def test_health_reports_llm_not_configured(make_client):
    response = make_client().get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "llm_configured": False}


def test_chat_returns_reply_and_new_thread_id(make_client):
    agent = FakeAgent()

    response = make_client(agent).post("/chat", json={"message": "  Hello  "})

    body = response.json()
    assert response.status_code == 200
    assert body["reply"] == "echo: Hello"
    assert re.fullmatch(r"[0-9a-f]{32}", body["thread_id"])
    assert agent.calls == [(body["thread_id"], "Hello")]


def test_chat_reuses_thread_id(make_client):
    agent = FakeAgent()
    client = make_client(agent)

    first = client.post("/chat", json={"message": "Hi"}).json()
    second = client.post("/chat", json={"message": "Again", "thread_id": first["thread_id"]})

    assert second.json()["thread_id"] == first["thread_id"]
    assert [thread for thread, _ in agent.calls] == [first["thread_id"]] * 2


@pytest.mark.parametrize(
    "payload",
    [
        {"message": ""},
        {"message": "   "},
        {},
        {"message": "x" * (MAX_MESSAGE_LENGTH + 1)},
        {"message": "Hi", "thread_id": ""},
    ],
)
def test_invalid_messages_are_rejected(make_client, payload):
    agent = FakeAgent()

    response = make_client(agent).post("/chat", json=payload)

    assert response.status_code == 422
    assert agent.calls == []


def test_chat_without_llm_configuration_answers_503(make_client):
    response = make_client().post("/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


@pytest.mark.parametrize("error", [LLMUnavailableError("timeout"), AgentStepLimitError("loop")])
def test_agent_failures_answer_503(make_client, error):
    response = make_client(FakeAgent(error=error)).post("/chat", json={"message": "Hello"})

    assert response.status_code == 503
    assert response.json()["detail"] == "The assistant could not answer right now, please try again"


def test_startup_assembles_real_agent_when_llm_is_configured(make_client):
    client = make_client(openrouter_api_key="test-key", llm_model="provider/model")

    controller = client.app.state.chat_controller

    assert isinstance(controller._agent, CustomerSupportAgent)
    assert client.get("/health").json()["llm_configured"] is True
