from fastapi import Request

from app.controllers.chat_controller import ChatController
from app.core.settings import Settings


def get_app_settings(request: Request) -> Settings:
    """Settings the application was created with."""
    return request.app.state.settings


def get_chat_controller(request: Request) -> ChatController:
    """Chat controller assembled at startup."""
    return request.app.state.chat_controller
