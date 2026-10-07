"""ElevenLabs text-to-speech. Returns MP3 bytes; the API key never leaves the backend."""
import logging
import re

import httpx

from app.config import settings
from app.models.schemas import ServiceError

logger = logging.getLogger("askit.tts")
MAX_SPOKEN_CHARS = 4500
# One valid silent MPEG-1 Layer III frame (128 kbps, 44.1 kHz) repeated ~1.5s: used in demo mode.
SILENT_MP3 = (b"\xff\xfb\x90\x64" + b"\x00" * 413) * 58


def clean_for_speech(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # [label](url) -> label
    text = re.sub(r"[#*_`>]+", "", text)
    text = re.sub(r"\n{2,}", ". ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > MAX_SPOKEN_CHARS:
        cut = text[:MAX_SPOKEN_CHARS]
        text = cut[: cut.rfind(". ") + 1] if ". " in cut else cut
    return text


def synthesize(text: str) -> bytes:
    if settings.demo_mode:
        return SILENT_MP3
    if not settings.elevenlabs_api_key or not settings.elevenlabs_voice_id:
        raise ServiceError("Text-to-speech is not configured (ELEVENLABS_API_KEY / ELEVENLABS_VOICE_ID).")
    logger.info("TTS started")
    try:
        resp = httpx.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}",
            headers={
                "xi-api-key": settings.elevenlabs_api_key,
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
            },
            json={"text": clean_for_speech(text), "model_id": "eleven_multilingual_v2"},
            timeout=60,
        )
    except httpx.TimeoutException:
        raise ServiceError("Text-to-speech timed out.", 504)
    except httpx.HTTPError:
        raise ServiceError("Could not reach the text-to-speech service.")
    if resp.status_code in (401, 403):
        raise ServiceError("Text-to-speech API key is invalid.")
    if resp.status_code == 429:
        raise ServiceError("Text-to-speech rate limit reached. Please try again shortly.", 429)
    if resp.status_code >= 400:
        logger.error("ElevenLabs returned HTTP %s", resp.status_code)
        raise ServiceError("Text-to-speech is temporarily unavailable (check ELEVENLABS_VOICE_ID).")
    logger.info("TTS completed (%d bytes)", len(resp.content))
    return resp.content
