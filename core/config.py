"""
Centralized configuration for B99 Quote Guesser.
All environment variables and settings are managed here.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # --- App ---
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:8000")
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"

    # --- B99 Quotes ---
    B99_MODE: str = os.environ.get("B99_MODE", "local")  # "local" or "api"
    B99_QUOTES_JSON: str | None = os.environ.get("B99_QUOTES_JSON") or "data/quotes.json"
    B99_API_URL: str = os.environ.get(
        "B99_API_URL", "https://brooklyn-nine-nine-quotes.herokuapp.com/api/v1"
    )

@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
