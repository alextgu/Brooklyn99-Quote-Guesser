"""
B99 Quotes API Client.
Fetches quotes from the Brooklyn Nine-Nine Quotes API for the game and daily challenges.
"""

import random
from dataclasses import dataclass
from typing import Optional
import httpx

from core.config import settings


@dataclass
class Quote:
    """Represents a quote from the B99 API."""

    character: str
    episode: str
    text: str

    @classmethod
    def from_api_response(cls, data: dict) -> "Quote":
        """Create a Quote from API response data."""
        return cls(
            character=data.get("Character", "Unknown"),
            episode=data.get("Episode", "Unknown"),
            text=data.get("QuoteText", ""),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "character": self.character,
            "episode": self.episode,
            "text": self.text,
        }

    def masked_text(self) -> str:
        """
        Returns the quote text with the speaker's name redacted.
        Prevents spoilers in the 'Who Said It?' game.
        """
        # Common patterns to mask
        masked = self.text
        if self.character:
            # Replace character name with [REDACTED]
            masked = masked.replace(f"{self.character}:", "[SPEAKER]:")
            masked = masked.replace(f"{self.character} ", "[SPEAKER] ")
        return masked


class B99QuotesClient:
    """Client for interacting with the Brooklyn Nine-Nine Quotes API."""

    def __init__(self, base_url: str | None = None, timeout: float = 10.0):
        self.base_url = base_url or settings.B99_API_URL
        self.timeout = timeout

    async def get_random_quote(self) -> Optional[Quote]:
        """Fetch a random quote from the API."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/quotes/random")
                response.raise_for_status()
                data = response.json()
                quote_data = data.get("Data")
                if quote_data:
                    return Quote.from_api_response(quote_data)
        except Exception as e:
            print(f"B99 API Error: {e}")
        return None

    async def get_random_quote_from_character(
        self, character: str
    ) -> Optional[Quote]:
        """Fetch a random quote from a specific character."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/quotes/random/from",
                    params={"character": character},
                )
                response.raise_for_status()
                data = response.json()
                quote_data = data.get("Data")
                if quote_data:
                    return Quote.from_api_response(quote_data)
        except Exception as e:
            print(f"B99 API Error: {e}")
        return None

    async def search_quotes(
        self, search_term: str, character: str | None = None
    ) -> list[Quote]:
        """Search for quotes containing a term, optionally filtered by character."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                params = {"searchTerm": search_term}
                if character:
                    params["character"] = character
                response = await client.get(
                    f"{self.base_url}/quotes/find", params=params
                )
                response.raise_for_status()
                data = response.json()
                quotes_data = data.get("Data", [])
                if quotes_data:
                    return [Quote.from_api_response(q) for q in quotes_data]
        except Exception as e:
            print(f"B99 API Error: {e}")
        return []

    async def get_characters(self) -> list[str]:
        """
        Get a list of main characters for the game.
        Since the API doesn't have a dedicated endpoint, we use a hardcoded list.
        """
        return [
            "Jake",
            "Amy",
            "Rosa",
            "Charles",
            "Captain Holt",
            "Sergeant Jeffords",
            "Gina",
            "Hitchcock",
            "Scully",
        ]


# Singleton client instance
quotes_client = B99QuotesClient()


# --- Synchronous wrappers for scripts ---
def get_random_quote_sync() -> Optional[Quote]:
    """Synchronous wrapper for getting a random quote (for use in scripts)."""
    import asyncio

    try:
        return asyncio.run(quotes_client.get_random_quote())
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return None
