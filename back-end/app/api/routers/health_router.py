from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_app_settings
from app.api.schemas.chat_schemas import HealthResponse
from app.core.settings import Settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health(settings: Annotated[Settings, Depends(get_app_settings)]) -> HealthResponse:
    """Report that the service is up and whether the LLM is configured."""
    return HealthResponse(llm_configured=settings.llm_configured)
