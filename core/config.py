"""
Centralized configuration for Holt Bot.
All environment variables and settings are managed here.
"""

import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # --- Supabase ---
    SUPABASE_URL: str | None = os.environ.get("SUPABASE_URL")
    SUPABASE_ANON_KEY: str | None = os.environ.get("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: str | None = os.environ.get("SUPABASE_SERVICE_KEY")

    # --- Resend ---
    RESEND_API_KEY: str | None = os.environ.get("RESEND_API_KEY")
    EMAIL_FROM: str = os.environ.get("EMAIL_FROM", "Holt <onboarding@resend.dev>")

    # --- App ---
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:8000")
    DEBUG: bool = os.environ.get("DEBUG", "false").lower() == "true"

    # --- B99 Quotes API ---
    B99_API_URL: str = os.environ.get(
        "B99_API_URL", "https://brooklyn-nine-nine-quotes.herokuapp.com/api/v1"
    )

    # --- Purge Settings ---
    PURGE_HOURS: int = int(os.environ.get("PURGE_HOURS", "48"))

    @property
    def supabase_configured(self) -> bool:
        """Check if Supabase is properly configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_ANON_KEY)

    @property
    def supabase_admin_configured(self) -> bool:
        """Check if Supabase admin (service key) is configured."""
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_KEY)

    @property
    def resend_configured(self) -> bool:
        """Check if Resend is properly configured."""
        return bool(self.RESEND_API_KEY)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Convenience alias
settings = get_settings()
