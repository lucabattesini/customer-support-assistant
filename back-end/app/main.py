import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agents.customer_support.factory import build_customer_support_agent
from app.api.routers import chat_router, health_router
from app.controllers.chat_controller import ChatController
from app.core.logging_config import configure_logging
from app.core.settings import Settings, get_settings
from app.core.store_config import load_store_config
from app.db.session import build_engine, build_session_factory, init_db

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create the API application.

    The database, tools and agent are assembled on startup. Without LLM credentials the
    application still starts: `/health` reports it and `/chat` answers 503.
    """
    app = FastAPI(title="Customer Support Assistant", lifespan=_lifespan)
    app.state.settings = settings or get_settings()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app.state.settings.cors_origin_list,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    app.include_router(health_router.router)
    app.include_router(chat_router.router)
    return app


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings: Settings = app.state.settings
    configure_logging(settings.log_level)
    engine = build_engine(settings.database_url)
    init_db(engine)
    store_config = load_store_config(settings.store_config_path)

    agent = None
    if settings.llm_configured:
        agent = build_customer_support_agent(settings, store_config, build_session_factory(engine))
    else:
        logger.warning("LLM is not configured; /chat will answer 503 until it is")

    app.state.chat_controller = ChatController(agent, settings.max_message_length)
    try:
        yield
    finally:
        engine.dispose()
