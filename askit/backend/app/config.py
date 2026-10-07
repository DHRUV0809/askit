"""Central configuration. Values are read from the environment on access."""
import os
from pathlib import Path

from dotenv import load_dotenv

_BACKEND = Path(__file__).resolve().parents[1]
load_dotenv(_BACKEND / ".env")
load_dotenv(_BACKEND.parent / ".env")  # project-root .env (never overrides existing vars)


def _bool(name: str) -> bool:
    return os.getenv(name, "false").strip().lower() in {"1", "true", "yes", "on"}


class Settings:
    max_query_length = 5000
    version = "1.0.0"

    @property
    def demo_mode(self) -> bool:
        return _bool("DEMO_MODE")

    @property
    def openai_api_key(self) -> str:
        return os.getenv("OPENAI_API_KEY", "").strip()

    @property
    def openai_model(self) -> str:
        return os.getenv("OPENAI_MODEL", "").strip() or "gpt-4o-mini"

    @property
    def tavily_api_key(self) -> str:
        return os.getenv("TAVILY_API_KEY", "").strip()

    @property
    def elevenlabs_api_key(self) -> str:
        return os.getenv("ELEVENLABS_API_KEY", "").strip()

    @property
    def elevenlabs_voice_id(self) -> str:
        return os.getenv("ELEVENLABS_VOICE_ID", "").strip()

    @property
    def frontend_url(self) -> str:
        return os.getenv("FRONTEND_URL", "http://localhost:5173").strip()

    @property
    def request_timeout(self) -> float:
        try:
            return float(os.getenv("REQUEST_TIMEOUT_SECONDS", "240"))
        except ValueError:
            return 240.0


settings = Settings()
