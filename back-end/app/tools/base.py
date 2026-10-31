import json
import logging
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sqlalchemy.orm import Session, sessionmaker

from app.core.clock import Clock
from app.core.store_config import StoreConfig
from app.db.session import session_scope
from app.domain.errors import DomainError
from app.services.container import ServiceContainer

logger = logging.getLogger(__name__)

Payload = dict[str, Any]


@dataclass(frozen=True)
class ToolContext:
    """Dependencies shared by every tool call."""

    session_factory: sessionmaker[Session]
    clock: Clock
    store_config: StoreConfig

    @contextmanager
    def services(self) -> Iterator[ServiceContainer]:
        """Open a database session for one tool call and expose the services bound to it."""
        with session_scope(self.session_factory) as session:
            yield ServiceContainer(session, self.store_config)


@dataclass(frozen=True)
class ToolSpec[InputT: BaseModel]:
    """Framework-independent definition of a tool."""

    name: str
    input_model: type[InputT]
    handler: Callable[[ToolContext, InputT], Payload]


def execute_tool[InputT: BaseModel](
    spec: ToolSpec[InputT], context: ToolContext, arguments: InputT
) -> str:
    """Run a tool and always return a JSON string, turning failures into error payloads.

    Expected business failures become `{"error": <code>, "action": <hint>, ...details}`.
    Unexpected exceptions are logged and returned as a generic error so the conversation
    can continue.
    """
    try:
        payload = spec.handler(context, arguments)
    except DomainError as error:
        payload = error_payload(error)
    except Exception:
        logger.exception("Tool %s failed", spec.name)
        payload = {"error": "internal_error", "action": "apologize_and_offer_handoff"}
    return to_json(payload)


def error_payload(error: DomainError) -> Payload:
    """Error response with the code, the suggested action and JSON-safe details."""
    return {"error": error.code, "action": error.action, **error.details}


def validation_error_payload(error: Exception) -> str:
    """Error response returned to the model when it sends invalid tool arguments."""
    errors = error.errors() if hasattr(error, "errors") else []
    return to_json(
        {
            "error": "invalid_arguments",
            "action": "fix_arguments_or_ask_customer",
            "fields": [
                {
                    "field": ".".join(str(part) for part in item.get("loc", ())),
                    "problem": item.get("msg"),
                }
                for item in errors
            ],
        }
    )


def to_json(payload: Payload) -> str:
    """Serialize a payload, keeping non-ASCII characters readable."""
    return json.dumps(payload, ensure_ascii=False)


def without_none(payload: Payload) -> Payload:
    """Drop keys whose value is None to keep tool responses short."""
    return {key: value for key, value in payload.items() if value is not None}
