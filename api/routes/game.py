"""
Game routes: 'Who Said It?' quote challenge.
Interactive engagement feature using B99 quotes.
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional

from core.quotes import quotes_client, Quote

router = APIRouter(prefix="/game", tags=["game"])

# Templates directory
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def game_page(request: Request):
    """
    Render the 'Who Said It?' game page.
    """
    return templates.TemplateResponse("game.html", {"request": request})


@router.get("/quote")
async def get_game_quote():
    """
    Get a random quote for the game.
    Returns the quote with the speaker name masked.
    
    Response:
    {
        "text": "[SPEAKER]: Something witty...",
        "episode": "Episode Name",
        "answer": "Character Name"  # For verification
    }
    """
    quote = await quotes_client.get_random_quote()

    if not quote:
        return {
            "error": "Could not fetch quote. Please try again.",
            "text": None,
            "episode": None,
            "answer": None,
        }

    return {
        "text": quote.masked_text(),
        "episode": quote.episode,
        "answer": quote.character,
    }


@router.get("/characters")
async def get_characters():
    """
    Get the list of characters for the autocomplete dropdown.
    """
    characters = await quotes_client.get_characters()
    return {"characters": characters}


@router.post("/verify")
async def verify_answer(guess: str = Query(...), answer: str = Query(...)):
    """
    Verify if the user's guess matches the correct answer.
    
    Args:
        guess: The user's guessed character name
        answer: The correct character name (from the original quote)
    
    Returns:
        {
            "correct": bool,
            "message": str
        }
    """
    # Case-insensitive comparison, handle partial matches
    guess_clean = guess.strip().lower()
    answer_clean = answer.strip().lower()

    # Allow partial matches (e.g., "Holt" matches "Captain Holt")
    correct = guess_clean == answer_clean or guess_clean in answer_clean or answer_clean in guess_clean

    if correct:
        messages = [
            "Correct. Your deductive skills are... adequate.",
            "Indeed. You have identified the speaker correctly.",
            "Affirmative. A satisfactory display of B99 knowledge.",
            "Correct. Captain Holt would approve of this precision.",
        ]
    else:
        messages = [
            f"Incorrect. The speaker was {answer}.",
            f"A regrettable error. It was {answer}.",
            f"Wrong. The quote belongs to {answer}.",
            f"Negative. {answer} spoke those words.",
        ]

    import random
    message = random.choice(messages)

    return {"correct": correct, "message": message, "actual_answer": answer}


@router.get("/search")
async def search_quotes(
    q: str = Query(..., min_length=2, description="Search term"),
    character: Optional[str] = Query(None, description="Filter by character"),
):
    """
    Deep-Search Autocomplete: Search quotes by text content.
    Used for exploring the quote database.
    """
    quotes = await quotes_client.search_quotes(q, character)

    return {
        "count": len(quotes),
        "quotes": [quote.to_dict() for quote in quotes[:10]],  # Limit to 10
    }
