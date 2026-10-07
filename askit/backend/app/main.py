import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import settings
from app.models.schemas import ServiceError

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("askit")

app = FastAPI(title="AskIt", version=settings.version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list({settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"}),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    msg = exc.errors()[0].get("msg", "Invalid request.") if exc.errors() else "Invalid request."
    msg = msg.removeprefix("Value error, ")
    return JSONResponse(status_code=400, content={"success": False, "error": msg})


@app.exception_handler(ServiceError)
async def service_handler(_: Request, exc: ServiceError):
    logger.warning("Service error: %s", exc.message)
    return JSONResponse(status_code=exc.status, content={"success": False, "error": exc.message})


@app.exception_handler(Exception)
async def unhandled_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error")  # stack trace stays in the server log
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Something went wrong. Please try again."},
    )


@app.get("/")
def root():
    return {"status": "online", "service": "AskIt", "version": settings.version}


@app.get("/health")
def health():
    return {"status": "healthy"}
