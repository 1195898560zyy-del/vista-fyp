from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.config import get_settings
from app.services.openai_service import transcribe_audio

router = APIRouter(prefix="/api")


class TranscribeBody(BaseModel):
    audio: str
    mime: str | None = "audio/webm"


@router.post("/transcribe")
async def transcribe(body: TranscribeBody, request: Request) -> dict[str, str]:
    if not body.audio:
        raise HTTPException(status_code=400, detail={"error": "Missing audio"})

    settings = get_settings()
    client = request.app.state.http_client
    try:
        text = await transcribe_audio(
            client, settings, audio_b64=body.audio, mime=body.mime or "audio/webm"
        )
        return {"text": text}
    except ValueError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail={"error": "Transcription failed"}) from exc
