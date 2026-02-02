"""
Bot logic for generating daily Holt messages.
Styled after Captain Holt's formal text messaging patterns.

Reference: Holt's scene reminding someone they are more than a number,
repeating their name with affirmations. Formal, no contractions,
name used frequently in that characteristic Holt cadence.
"""

import random

# Opening lines (sets the context)
OPENERS = [
    "{name}, I must remind you of something important.",
    "{name}. I have been meaning to tell you this.",
    "It has come to my attention, {name}, that you may need a reminder.",
    "{name}, allow me to state some facts.",
    "I am writing to you today, {name}, because you need to hear this.",
    "{name}. Listen carefully.",
]

# Affirmation lines - each ends with the name for that repetitive Holt cadence
# These are mixed and 5 are chosen randomly
AFFIRMATIONS = [
    "You are not merely a statistic, {name}.",
    "You are more than just a number, {name}.",
    "You are capable of extraordinary things, {name}.",
    "You are resilient, {name}.",
    "You are not defined by your setbacks, {name}.",
    "You are stronger than you realize, {name}.",
    "You are worthy of success, {name}.",
    "You are not alone in this endeavor, {name}.",
    "You are making progress, {name}.",
    "You are precisely where you need to be, {name}.",
    "You are someone who finishes what they start, {name}.",
    "You are a person of value, {name}.",
    "You are not your worst day, {name}.",
    "You are improving with each passing moment, {name}.",
    "You are demonstrating admirable fortitude, {name}.",
    "You are exceeding expectations, {name}.",
    "You are building something meaningful, {name}.",
    "You are the architect of your own success, {name}.",
    "You are disciplined, {name}.",
    "You are persistent, {name}.",
    "You are {name}.",
]

# Closings (heavy on name usage)
CLOSINGS = [
    "That is all, {name}. Remember this, {name}.",
    "Do not forget this, {name}. You are {name}.",
    "Remember who you are, {name}. You are {name}.",
    "Proceed with confidence, {name}. I believe in you, {name}.",
    "I believe in you, {name}. That is not something I say lightly, {name}.",
    "Now go forth, {name}. You are ready, {name}.",
    "You have my full support, {name}. Always, {name}.",
    "This is the truth, {name}. Accept it, {name}.",
]


def generate_holt_message(name: str, day_count: int) -> str:
    """
    Generates a daily Captain Holt-styled motivational message.
    
    The message mimics Holt's repetitive affirmation style:
    - 5 lines of "You are [quality], [Name]."
    - Uses the recipient's name frequently (Holt's signature move)
    - No contractions
    - Formal, supportive, repetitive cadence
    
    Args:
        name: The user's name
        day_count: Number of days since signup
        
    Returns:
        A formatted message string in Holt's style
    """
    # Use name + day as seed for consistency (same message each day for same user)
    random.seed(f"{name}-{day_count}")
    
    # Build the message
    opener = random.choice(OPENERS).format(name=name, day=day_count)
    
    # Pick 5 random affirmations (no repeats)
    chosen_affirmations = random.sample(AFFIRMATIONS, 5)
    affirmation_lines = [a.format(name=name) for a in chosen_affirmations]
    
    closing = random.choice(CLOSINGS).format(name=name, day=day_count)
    
    # Reset random seed
    random.seed()
    
    # Format: opener, blank line, 5 affirmations, blank line, closing, signature
    affirmations_block = "\n".join(affirmation_lines)
    
    message = f"""{opener}

{affirmations_block}

{closing}

Sincerely,
Captain Raymond Holt"""

    return message


def generate_game_prompt(name: str) -> str:
    """
    Generate a Holt-styled prompt for the daily game.
    
    Args:
        name: The user's name
        
    Returns:
        A formal invitation to play the quote game
    """
    prompts = [
        f"{name}, I have prepared a challenge for you. Identify which member of the Nine-Nine spoke the following words.",
        f"Additionally, {name}, I present you with today's intellectual exercise. Name the speaker.",
        f"{name}, your daily assessment awaits below. Demonstrate your knowledge of the precinct.",
        f"Now, {name}, for today's game: identify the individual who uttered this statement.",
        f"I have selected a quote for your consideration, {name}. Determine its origin.",
    ]
    
    random.seed(f"{name}-game-prompt")
    prompt = random.choice(prompts)
    random.seed()
    
    return prompt
