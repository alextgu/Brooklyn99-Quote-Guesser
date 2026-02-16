"""
Game routes: 'Who Said It?' quote challenge.
Brooklyn 99 quote guesser.
"""

from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from typing import Optional

from core.quotes import quotes_client, Quote, get_canonical_character

router = APIRouter(prefix="/game", tags=["game"])

# Templates directory
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/quote")
async def get_game_quote(hard_mode: bool = False):
    """
    Get a random quote for the game.
    
    Args:
        hard_mode: If true, hides episode name (player must guess character + episode)
    
    Response:
    {
        "text": "[SPEAKER]: Something witty...",
        "episode": "Episode Name" or null (if hard_mode),
        "season": 1-8 or null,
        "answer_character": "Character Name",
        "answer_episode": "Episode Name",
        "answer_season": 1-8 or null
    }
    """
    quote = await quotes_client.get_random_quote()

    if not quote:
        return {
            "error": "Could not fetch quote. Please try again.",
            "text": None,
            "episode": None,
            "season": None,
            "answer_character": None,
            "answer_episode": None,
            "answer_season": None,
        }

    return {
        "text": quote.masked_text(),
        "episode": None if hard_mode else quote.episode,
        "season": None if hard_mode else quote.season,
        "answer_character": quote.character,
        "answer_episode": quote.episode,
        "answer_season": quote.season,
    }


@router.get("/characters")
async def get_characters():
    """
    Get the list of characters for the autocomplete dropdown.
    """
    characters = await quotes_client.get_characters()
    return {"characters": characters}


@router.get("/episodes")
async def get_episodes(season: Optional[int] = None):
    """
    Get episodes, optionally filtered by season.
    Returns dict of season -> episode list for dropdowns.
    """
    from core.episodes import EPISODE_SEASONS, get_episodes_by_season
    
    if season:
        return {"episodes": get_episodes_by_season(season)}
    
    # Return all episodes grouped by season
    episodes_by_season = {}
    for ep, s in EPISODE_SEASONS.items():
        if s not in episodes_by_season:
            episodes_by_season[s] = []
        if ep not in episodes_by_season[s]:  # Avoid duplicates
            episodes_by_season[s].append(ep)
    
    # Sort episodes within each season
    for s in episodes_by_season:
        episodes_by_season[s] = sorted(set(episodes_by_season[s]))
    
    return {"episodes_by_season": episodes_by_season}


@router.get("/seasons")
async def get_seasons():
    """
    Get the list of seasons (1-8).
    """
    return {"seasons": list(range(1, 9))}


@router.post("/verify")
async def verify_answer(
    guess_character: str = Query(..., alias="guess"),
    answer_character: str = Query(..., alias="answer"),
    guess_episode: Optional[str] = Query(None),
    answer_episode: Optional[str] = Query(None),
    guess_season: Optional[int] = Query(None),
    answer_season: Optional[int] = Query(None),
):
    """
    Verify if the user's guess matches the correct answer.
    
    Always checks character. If episode data is provided, also checks episode.
    
    Returns:
        {
            "correct": bool (all provided fields match),
            "character_correct": bool,
            "episode_correct": bool,
            "message": str
        }
    """
    import random
    
    # Check character: use alias mapping (e.g. "Pontiac Bandit" -> "Doug Judy")
    guess_char_clean = guess_character.strip().lower()
    answer_char_clean = answer_character.strip().lower()
    guess_canonical = get_canonical_character(guess_character)
    if guess_canonical:
        character_correct = guess_canonical.lower() == answer_char_clean
    else:
        # Fallback: substring match for characters not in alias map
        character_correct = (
            guess_char_clean == answer_char_clean
            or guess_char_clean in answer_char_clean
            or answer_char_clean in guess_char_clean
        )
    
    # Check episode if provided (exact match on episode name)
    episode_correct = False
    if guess_episode and answer_episode:
        guess_ep_clean = guess_episode.strip().lower()
        answer_ep_clean = answer_episode.strip().lower()
        episode_correct = guess_ep_clean == answer_ep_clean
    elif not guess_episode and answer_episode:
        # No guess provided but answer exists = wrong
        episode_correct = False
    else:
        # No episode to check = consider it correct (not applicable)
        episode_correct = True
    
    # Overall: both must be correct
    all_correct = character_correct and episode_correct
    
    # Generate message
    if all_correct:
        messages = [
            "Correct. Your deductive skills are... adequate.",
            "Indeed. You have identified the speaker and episode correctly.",
            "Affirmative. A satisfactory display of B99 knowledge.",
            "Exceptional. Captain Holt would be... mildly impressed.",
        ]
    else:
        messages = [
            f"Incorrect. The speaker was {answer_character} in '{answer_episode}'.",
            f"A regrettable error. It was {answer_character}, episode: {answer_episode}.",
            f"Negative. {answer_character} spoke those words in '{answer_episode}'.",
        ]
    
    message = random.choice(messages)

    return {
        "correct": all_correct,
        "character_correct": character_correct,
        "episode_correct": episode_correct,
        "message": message,
        "actual_character": answer_character,
        "actual_episode": answer_episode,
    }


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
