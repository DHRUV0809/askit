import asyncio
import logging
import time

from fastapi import APIRouter
from fastapi.responses import Response

from app.config import settings
from app.models.schemas import AskRequest, AskResponse, ServiceError, TTSRequest
from app.services.research_service import run_research
from app.services.tts_service import synthesize

logger = logging.getLogger("askit.api")
router = APIRouter(prefix="/api")


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    start = time.perf_counter()
    logger.info("Incoming /api/ask (%d chars)", len(req.query))
    try:
        answer, sources = await asyncio.wait_for(
            asyncio.to_thread(run_research, req.query), timeout=settings.request_timeout
        )
    except asyncio.TimeoutError:
        logger.error("Research timed out")
        raise ServiceError("Research took too long. Please try a simpler question.", 504)
    elapsed = round(time.perf_counter() - start, 2)
    logger.info("Request completed in %.2fs", elapsed)
    return AskResponse(query=req.query, answer=answer, sources=sources, processing_time=elapsed)


@router.post("/tts")
async def tts(req: TTSRequest) -> Response:
    logger.info("Incoming /api/tts (%d chars)", len(req.text))
    audio = await asyncio.to_thread(synthesize, req.text)
    return Response(content=audio, media_type="audio/mpeg")
