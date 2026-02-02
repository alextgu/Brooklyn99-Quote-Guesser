"""
Brooklyn 99 Quotes Fetcher.
Loads quotes from a local JSON file for the 'Who Said It?' game.
"""

import json
import random
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from core.config import settings
from core.episodes import get_season


# Character name aliases (character -> all name variations)
# Built from all 47 unique characters in the quotes database
CHARACTER_ALIASES = {
    # Main cast
    "Jake": ["Jake", "Peralta", "Jake Peralta"],
    "Amy": ["Amy", "Santiago", "Amy Santiago"],
    "Rosa": ["Rosa", "Diaz", "Rosa Diaz"],
    "Charles": ["Charles", "Boyle", "Charles Boyle"],
    "Sergeant Jeffords": ["Terry", "Jeffords", "Terry Jeffords", "Sergeant Jeffords", "Sarge"],
    "Gina": ["Gina", "Linetti", "Gina Linetti"],
    "Captain Holt": ["Holt", "Captain Holt", "Raymond", "Raymond Holt", "Captain Raymond Holt"],
    "Kevin": ["Kevin", "Cozner", "Kevin Cozner"],
    "Hitchcock": ["Hitchcock", "Michael Hitchcock"],
    "Scully": ["Scully", "Norm Scully"],
    
    # Recurring characters
    "Doug Judy": ["Doug Judy", "Judy", "Doug", "The Pontiac Bandit", "Pontiac Bandit"],
    "Trudy Judy": ["Trudy Judy", "Trudy"],
    "Madeline Wuntch": ["Wuntch", "Madeline", "Madeline Wuntch", "Deputy Chief Wuntch"],
    "Adrian Pimento": ["Adrian", "Pimento", "Adrian Pimento"],
    "The Vulture": ["The Vulture", "Vulture", "Pembroke", "Keith Pembroke"],
    "Captain C.J. Jason Stentley": ["CJ", "Captain CJ", "Captain C.J. Jason Stentley", "Stentley"],
    "Officer Debbie Fogle": ["Debbie", "Fogle", "Foggle", "Debbie Fogle", "Debbie Foggle", "Officer Fogle", "Officer Debbie Fogle"],
    "Teddy": ["Teddy", "Teddy Wells"],
    "Sophia": ["Sophia", "Sophia Perez"],
    "Genevieve": ["Genevieve"],
    "Nikolaj Boyle": ["Nikolaj", "Nikolaj Boyle"],
    "Dillman": ["Dillman"],
    
    # Family members
    "Karen Peralta": ["Karen", "Karen Peralta"],
    "Roger Peralta": ["Roger", "Roger Peralta"],
    "Walter Peralta": ["Walter", "Walter Peralta"],
    "Katie Peralta": ["Katie", "Katie Peralta"],
    "Victor Santiago": ["Victor", "Victor Santiago"],
    "Camila Santiago": ["Camila", "Camila Santiago"],
    "David Santiago": ["David", "David Santiago"],
    "Darlene Linetti": ["Darlene", "Darlene Linetti"],
    "Lynn Boyle": ["Lynn", "Lynn Boyle"],
    
    # Minor/guest characters
    "Adam Jarver": ["Adam", "Jarver", "Adam Jarver"],
    "Beefer": ["Beefer"],
    "Bill": ["Bill"],
    "Cindy Shatz": ["Cindy", "Shatz", "Cindy Shatz"],
    "Detective Lohank": ["Lohank", "Detective Lohank"],
    "Emily": ["Emily"],
    "Gintars": ["Gintars"],
    "Gordon Lundt": ["Gordon", "Lundt", "Gordon Lundt"],
    "Jess": ["Jess"],
    "Keri Brennan": ["Keri", "Brennan", "Keri Brennan"],
    "Milton": ["Milton"],
    "Pam": ["Pam"],
    "Sheriff Reynolds": ["Reynolds", "Sheriff Reynolds"],
}

# Build flat list of all character names for masking
ALL_CHARACTERS = sorted(
    set(name for aliases in CHARACTER_ALIASES.values() for name in aliases),
    key=len, reverse=True
)


def get_speaker_aliases(character: str) -> set[str]:
    """Get all name variations for a character."""
    aliases = set()
    char_lower = character.lower().strip()
    
    # Check each alias group
    for main_name, name_list in CHARACTER_ALIASES.items():
        name_list_lower = [n.lower() for n in name_list]
        if char_lower in name_list_lower or char_lower == main_name.lower():
            aliases.update(n.lower() for n in name_list)
            break
    
    # Fallback: use the character name and its parts
    if not aliases:
        aliases.add(char_lower)
        for part in character.split():
            if len(part) > 2:
                aliases.add(part.lower())
    
    return aliases


@dataclass
class Quote:
    """Represents a Brooklyn 99 quote."""
    character: str
    episode: str
    text: str
    header: str
    season: int | None = field(default=None)
    
    def masked_text(self) -> str:
        """
        Return the quote with ALL character names masked.
        - Main speaker (self.character) → [SPEAKER]
        - All other characters → [CHARACTER]
        
        Uses multiple strategies:
        1. Known character names from CHARACTER_ALIASES
        2. Any "Name:" pattern (dialogue attribution)
        3. Common B99 guest character names
        4. Names that appear to be proper nouns in context
        """
        masked = self.text
        
        # Get all name variations for the main speaker (the answer)
        speaker_names = get_speaker_aliases(self.character) if self.character else set()
        
        # Extra guest/minor character names not in main list
        EXTRA_NAMES = {
            "Esther", "Kurm", "Dustin", "Shaw", "Figi", "Marcus", "Frederick",
            "Seamus", "Murphy", "Figgis", "Jimmy", "Kelly", "Dozerman",
            "Parlov", "Romero", "Jason", "Derek", "Mlepnos", "Mlep", 
            "Stevie", "Steve", "Melanie", "Hawkins", "Veronica", "Bob",
            "Mervyn", "Carl", "Tommy", "Johnny", "Billy", "Eddie", "Jimmy",
            "George", "Frank", "Harry", "Jack", "Joe", "Mike", "Nick",
            "Paul", "Pete", "Phil", "Rick", "Sam", "Tim", "Tom", "Tony",
            "Sal", "Vinny", "Danny", "Kenny", "Larry", "Gary", "Jerry",
            "Barry", "Terry", "Mary", "Nancy", "Sarah", "Rachel", "Linda",
            "Susan", "Barbara", "Lisa", "Betty", "Helen", "Sandra", "Donna",
            "Carol", "Ruth", "Sharon", "Michelle", "Laura", "Cagney", "Lacey",
            "O'Sullivan", "Sullivan",
        }
        
        # Step 1: Find any "Name:" patterns to discover unknown character names
        name_colon_pattern = re.compile(r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s*:')
        discovered_names = set()
        for match in name_colon_pattern.finditer(self.text):
            name = match.group(1)
            if name.lower() not in speaker_names:
                discovered_names.add(name)
        
        # Step 2: Replace main speaker's name variations with temporary placeholder
        for name in sorted(speaker_names, key=len, reverse=True):
            if len(name) > 2:
                pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                masked = pattern.sub("__SPEAKER__", masked)
        
        # Step 3: Replace all known character names with [CHARACTER]
        for char_name in ALL_CHARACTERS:
            if char_name.lower() not in speaker_names and len(char_name) > 2:
                pattern = re.compile(r'\b' + re.escape(char_name) + r'\b', re.IGNORECASE)
                masked = pattern.sub("[CHARACTER]", masked)
        
        # Step 4: Replace extra guest character names
        for name in EXTRA_NAMES:
            if name.lower() not in speaker_names:
                pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                masked = pattern.sub("[CHARACTER]", masked)
        
        # Step 5: Replace discovered names (from "Name:" patterns) EVERYWHERE in quote
        for name in sorted(discovered_names, key=len, reverse=True):
            if len(name) > 2:
                pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                masked = pattern.sub("[CHARACTER]", masked)
        
        # Step 6: Convert temporary placeholder to [SPEAKER]
        masked = masked.replace("__SPEAKER__", "[SPEAKER]")
        
        return masked
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "character": self.character,
            "episode": self.episode,
            "season": self.season,
            "text": self.text,
            "header": self.header,
        }


class QuotesClient:
    """Client for fetching Brooklyn 99 quotes."""
    
    def __init__(self):
        self.quotes: list[Quote] = []
        self.quotes_by_character: dict[str, list[Quote]] = {}
        self._characters: list[str] = []
        self._load_quotes()
    
    def _load_quotes(self):
        """Load quotes from the configured source."""
        if settings.B99_MODE == "local":
            self._load_from_json()
        else:
            print("API mode not yet implemented, falling back to local")
            self._load_from_json()
    
    def _load_from_json(self):
        """Load quotes from local JSON file."""
        json_path = settings.B99_QUOTES_JSON
        
        if not json_path:
            print("Warning: B99_QUOTES_JSON not configured")
            return
        
        path = Path(json_path)
        if not path.exists():
            print(f"Warning: Quotes file not found at {json_path}")
            return
        
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            
            raw_quotes = data.get("root", [])
            
            for q in raw_quotes:
                character = q.get("Character", "Unknown").strip()
                episode = q.get("Episode", "Unknown")
                quote = Quote(
                    character=character,
                    episode=episode,
                    text=q.get("QuoteText", ""),
                    header=q.get("Header", ""),
                    season=get_season(episode),
                )
                self.quotes.append(quote)
                
                # Index by character
                if character not in self.quotes_by_character:
                    self.quotes_by_character[character] = []
                self.quotes_by_character[character].append(quote)
            
            # Build sorted character list
            self._characters = sorted(self.quotes_by_character.keys())
            
            print(f"Loaded {len(self.quotes)} quotes from {len(self._characters)} characters")
        except Exception as e:
            print(f"Error loading quotes: {e}")
    
    async def get_random_quote(self, character: Optional[str] = None) -> Optional[Quote]:
        """Get a random quote, optionally filtered by character."""
        if character:
            quotes = self.quotes_by_character.get(character, [])
        else:
            quotes = self.quotes
        
        if not quotes:
            return None
        
        return random.choice(quotes)
    
    async def get_characters(self) -> list[str]:
        """Get list of all characters with quotes."""
        return self._characters
    
    async def search_quotes(self, query: str, character: Optional[str] = None) -> list[Quote]:
        """
        Search quotes by text content.
        
        Args:
            query: Search term
            character: Optional character filter
        """
        query_lower = query.lower()
        results = []
        
        source = self.quotes_by_character.get(character, []) if character else self.quotes
        
        for quote in source:
            if query_lower in quote.text.lower():
                results.append(quote)
        
        return results
    
    def get_quote_for_day(self, name: str, day_count: int, character: Optional[str] = None) -> Optional[Quote]:
        """
        Get a consistent quote for a user's day (same user + day = same quote).
        Synchronous version for daily emails.
        """
        if character:
            quotes = self.quotes_by_character.get(character, [])
        else:
            quotes = self.quotes
        
        if not quotes:
            return None
        
        random.seed(f"{name}-{day_count}-quote")
        quote = random.choice(quotes)
        random.seed()
        
        return quote
    
    def get_quote_count(self, character: Optional[str] = None) -> int:
        """Get total number of quotes."""
        if character:
            return len(self.quotes_by_character.get(character, []))
        return len(self.quotes)


# Singleton instance
quotes_client = QuotesClient()


def get_random_quote_sync() -> Optional[Quote]:
    """
    Get a random quote for today - UNIVERSAL for all users.
    Uses today's date as seed so the same quote is returned all day.
    
    This ensures all newsletter recipients get the same daily challenge.
    """
    from datetime import date
    
    quotes = quotes_client.quotes
    if not quotes:
        return None
    
    # Seed with today's date for consistency across all users
    today = date.today().isoformat()
    random.seed(f"daily-quote-{today}")
    quote = random.choice(quotes)
    random.seed()
    
    return quote
