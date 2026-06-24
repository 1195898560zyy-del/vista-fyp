"""Speech-to-text endpoint — OpenAI Whisper."""

from fastapi import APIRouter

from app.deps import HttpClient, SettingsDep
from app.errors import api_error
from app.routers.helpers import handle_service_errors
from app.schemas.agent import TranscribeRequest
from app.services import openai_client

router = APIRouter(prefix="/api", tags=["transcribe"])


@router.post("/transcribe")
@handle_service_errors
async def transcribe(client: HttpClient, settings: SettingsDep, body: TranscribeRequest):
    if not body.audio:
        raise api_error("Missing audio")
    text = await openai_client.transcribe_audio(
        client,
        settings,
        audio_b64=body.audio,
        mime=body.mime or "audio/webm",
    )
    return {"text": text}
