from pydantic import BaseModel, field_validator

MAX_QUERY = 5000
MAX_TTS_TEXT = 10000


class ServiceError(Exception):
    """A user-presentable failure (never contains secrets or stack traces)."""

    def __init__(self, message: str, status: int = 503):
        super().__init__(message)
        self.message = message
        self.status = status


def _clean(value: str, limit: int, label: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{label} must not be empty.")
    if len(value) > limit:
        raise ValueError(f"{label} is too long (maximum {limit} characters).")
    return value


class AskRequest(BaseModel):
    query: str

    @field_validator("query")
    @classmethod
    def _v(cls, v: str) -> str:
        return _clean(v, MAX_QUERY, "Query")


class TTSRequest(BaseModel):
    text: str

    @field_validator("text")
    @classmethod
    def _v(cls, v: str) -> str:
        return _clean(v, MAX_TTS_TEXT, "Text")


class Source(BaseModel):
    title: str
    url: str


class AskResponse(BaseModel):
    success: bool = True
    query: str
    answer: str
    sources: list[Source] = []
    processing_time: float
