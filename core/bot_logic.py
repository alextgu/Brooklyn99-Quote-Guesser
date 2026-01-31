"""
Bot logic for generating daily Holt messages.
Uses unusual pools of phrases: openers, chants, and reflections.
"""

import random

# Unusual phrase pools
OPENERS = [
    "The morning fog parts, revealing your path",
    "A peculiar wind stirs the leaves today",
    "The old clock tower chimes for you alone",
    "Somewhere, a lighthouse blinks in your honor",
    "The universe hums a frequency only you can hear",
    "A raven lands on a wire, watching with knowing eyes",
    "The tide shifts, carrying whispers of your name",
    "An ancient tree bends slightly in your direction",
    "The stars rearranged themselves last night for you",
    "A forgotten bell rings in a distant valley",
]

CHANTS = [
    "Forward, ever forward, through the mist",
    "One step, then another, then the mountain moves",
    "The river does not stop; neither shall you",
    "Breathe deep the strange air of becoming",
    "Let the old skin fall; the new one fits better",
    "The fire burns low but never dies",
    "Roots grow deeper in darkness",
    "The owl asks 'who' but you already know",
    "Silence is the loudest teacher",
    "The path appears only when you walk",
]

REFLECTIONS = [
    "Consider: what grows when you are not looking?",
    "The mirror shows today, not tomorrow",
    "Every ending is a door painted to look like a wall",
    "You have survived every day so far. The odds are good.",
    "The seeds you planted in confusion bloom in clarity",
    "Rest is not retreat; it is preparation",
    "Your shadow proves you stand in light",
    "The longest journeys begin with forgetting the map",
    "What feels like loss is often rearrangement",
    "The universe is not against you; it is indifferent, and that is freedom",
]


def generate_holt_message(name: str, day_count: int) -> str:
    """
    Generates a daily message for a user based on their day count.
    Combines an opener, a chant, and a reflection into an unusual daily dispatch.
    
    Args:
        name: The user's name
        day_count: Number of days since signup
        
    Returns:
        A formatted message string
    """
    # Use day_count as seed component for some consistency, but add randomness
    random.seed(f"{name}-{day_count}")
    
    opener = random.choice(OPENERS)
    chant = random.choice(CHANTS)
    reflection = random.choice(REFLECTIONS)
    
    # Reset random seed to not affect other random calls
    random.seed()
    
    message = f"""Greetings, {name}.

Day {day_count} of your journey.

{opener}.

{chant}.

{reflection}

Until tomorrow,
— Holt"""

    return message
