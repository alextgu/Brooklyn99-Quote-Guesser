"""
Brooklyn 99 Episode to Season mapping.
Used for the harder game mode where players guess season + episode.
"""

# Episode name -> Season number mapping
EPISODE_SEASONS = {
    # Season 1
    "Pilot": 1,
    "The Tagger": 1,
    "The Slump": 1,
    "M.E. Time": 1,
    "The Vulture": 1,
    "Halloween": 1,
    "48 Hours": 1,
    "Old School": 1,
    "Sal's Pizza": 1,
    "Thanksgiving": 1,
    "Christmas": 1,
    "Pontiac Bandit": 1,
    "The Bet": 1,
    "The Ebony Falcon": 1,
    "Operation Broken Feather": 1,
    "The Party": 1,
    "Full Boyle": 1,
    "The Apartment": 1,
    "Tactical Village": 1,
    "Fancy Brudgom": 1,
    "Unsolvable": 1,
    "Charges and Specs": 1,
    
    # Season 2
    "Payback": 2,
    "Undercover": 2,
    "Chocolate Milk": 2,
    "The Jimmy Jab Games": 2,
    "Halloween II": 2,
    "The Mole": 2,
    "Jake and Sophia": 2,
    "Lockdown": 2,
    "USPIS": 2,
    "The Road Trip": 2,
    "The Pontiac Bandit Returns": 2,
    "Stakeout": 2,
    "Beach House": 2,
    "Defense Rests": 2,
    "Captain Peralta": 2,
    "Windbreaker City": 2,
    "The Wednesday Incident": 2,
    "Boyle-Linetti Wedding": 2,
    "Captain Peralta": 2,
    "Sabotage": 2,
    "AC/DC": 2,
    "Det. Dave Majors": 2,
    "The Chopper": 2,
    "Johnny and Dora": 2,
    
    # Season 3
    "New Captain": 3,
    "The Funeral": 3,
    "Boyle's Hunch": 3,
    "The Oolong Slayer": 3,
    "Halloween III": 3,
    "Into the Woods": 3,
    "The Mattress": 3,
    "Ava": 3,
    "The Swedes": 3,
    "Yippie Kayak": 3,
    "Hostage Situation": 3,
    "9 Days": 3,
    "The Cruise": 3,
    "Karen Peralta": 3,
    "The 9-8": 3,
    "House Mouses": 3,
    "Adrian Pimento": 3,
    "Cheddar": 3,
    "Terry Kitties": 3,
    "Paranoia": 3,
    "Maximum Security": 3,
    "Bureau": 3,
    "Greg and Larry": 3,
    
    # Season 4
    "The Audit": 4,
    "The Slaughterhouse": 4,
    "Coral Palms Pt. 1": 4,
    "Coral Palms Pt. 2": 4,
    "Coral Palms Pt. 3": 4,
    "The Night Shift": 4,
    "Halloween IV": 4,
    "Monster in the Closet": 4,
    "Mr. Santiago": 4,
    "Skyfire Cycle": 4,
    "The Overmining": 4,
    "Captain Latvia": 4,
    "The Fugitive Pt. 1": 4,
    "The Fugitive Pt. 2": 4,
    "The Fugitive (Part 1)": 4,
    "The Fugitive (Part 2)": 4,
    "Serve & Protect": 4,
    "Moo Moo": 4,
    "Cop-Con": 4,
    "Chasing Amy": 4,
    "Your Honor": 4,
    "The Last Ride": 4,
    "The Bank Job": 4,
    "Crime & Punishment": 4,
    "Charges and Specs": 4,
    
    # Season 5
    "The Big House Pt.1": 5,
    "The Big House Pt. 2": 5,
    "Kicks": 5,
    "HalloVeen": 5,
    "Bad Beat": 5,
    "The Venue": 5,
    "Two Turkeys": 5,
    "Return to Skyfire": 5,
    "99": 5,
    "Game Night": 5,
    "The Favor": 5,
    "Safe House": 5,
    "The Negotiation": 5,
    "The Box": 5,
    "The Puzzle Master": 5,
    "NutriBoom": 5,
    "DFW": 5,
    "Gray Star Mutual": 5,
    "Bachelor/ette Party": 5,
    "Show Me Going": 5,
    "White Whale": 5,
    "Jake & Amy": 5,
    
    # Season 6
    "The Honeypot": 6,
    "Honeymoon": 6,
    "Hitchcock & Scully": 6,
    "The Tattler": 6,
    "Four Movements": 6,
    "A Tale of Two Bandits": 6,
    "The Crime Scene": 6,
    "The Therapist": 6,
    "He Said, She Said": 6,
    "The Golden Child": 6,
    "Gintars": 6,
    "The Therapist": 6,
    "Casecation": 6,
    "The Bimbo": 6,
    "Ticking Clocks": 6,
    "Return of the King": 6,
    "Cinco De Mayo": 6,
    "Sicko": 6,
    "Suicide Squad": 6,
    
    # Season 7
    "Manhunter": 7,
    "Captain Kim": 7,
    "Pimento": 7,
    "The Jimmy Jab Games II": 7,
    "Debbie": 7,
    "Trying": 7,
    "Ding Dong": 7,
    "The Takeback": 7,
    "Dillman": 7,
    "Admiral Peralta": 7,
    "Valloweaster": 7,
    "Ransom": 7,
    "Lights Out": 7,
    
    # Season 8
    "The Good Ones": 8,
    "The Lake House": 8,
    "Blue Flu": 8,
    "Balancing": 8,
    "PB&J": 8,
    "The Set Up": 8,
    "Game of Boyles": 8,
    "Renewal": 8,
    "The Last Day Pt. 1": 8,
    "The Last Day Pt. 2": 8,
    "The Last Day (Part 1)": 8,
    "The Last Day (Part 2)": 8,
}


def get_season(episode_name: str) -> int | None:
    """
    Get the season number for an episode.
    Returns None if episode not found.
    """
    if not episode_name:
        return None
    
    # Try exact match first
    if episode_name in EPISODE_SEASONS:
        return EPISODE_SEASONS[episode_name]
    
    # Try case-insensitive match
    episode_lower = episode_name.lower().strip()
    for ep, season in EPISODE_SEASONS.items():
        if ep.lower() == episode_lower:
            return season
    
    return None


def get_all_episodes() -> list[str]:
    """Get list of all known episodes."""
    return sorted(set(EPISODE_SEASONS.keys()))


def get_episodes_by_season(season: int) -> list[str]:
    """Get all episodes from a specific season."""
    return [ep for ep, s in EPISODE_SEASONS.items() if s == season]
