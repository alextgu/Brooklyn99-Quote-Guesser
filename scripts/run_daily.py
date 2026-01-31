#!/usr/bin/env python3
"""
Daily Dispatch Engine for Holt Bot.

This script:
1. Connects to Supabase using the SERVICE_KEY (bypasses RLS)
2. Fetches all confirmed users who haven't been notified today
3. Fetches a random B99 quote for the daily challenge
4. Generates a personalized Holt message with the quote challenge
5. Sends the daily email
6. Updates last_notified_at to prevent duplicate sends (Anti-Duplicate Guard)

Run manually: python scripts/run_daily.py
Schedule with GitHub Actions: 0 8 * * * (The Morning Alarm)
"""

import sys
from datetime import date

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from core.database import (
    get_confirmed_users_for_dispatch,
    update_last_notified,
    calculate_day_count,
)
from core.bot_logic import generate_holt_message
from core.quotes import get_random_quote_sync
from core.mailer import send_daily_email


def build_daily_message(name: str, day_count: int) -> str:
    """
    Build the complete daily message with:
    1. Quote of the Day challenge
    2. Personalized Holt compliment
    """
    # Get the Holt compliment
    holt_message = generate_holt_message(name, day_count)

    # Get a random B99 quote for the challenge
    quote = get_random_quote_sync()

    if quote:
        # Mask the speaker name for the challenge
        challenge_section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 TODAY'S CHALLENGE: "Who Said It?"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Episode: {quote.episode}

"{quote.masked_text()}"

Can you identify the speaker? 
Visit the website to submit your answer.
"""
    else:
        challenge_section = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📺 QUOTE SERVICE UNAVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The quote retrieval system is temporarily offline.
Captain Holt is... displeased.
"""

    # Combine the sections
    full_message = f"""{holt_message}

{challenge_section}
"""
    return full_message


def run_daily_dispatch():
    """
    Main dispatcher function. Fetches users and sends daily messages.
    """
    print(f"[{date.today()}] Starting daily dispatch...")

    # 1. Get all confirmed users who need notification
    users = get_confirmed_users_for_dispatch()

    if not users:
        print("No users to notify today.")
        return 0

    print(f"Found {len(users)} user(s) to notify.")

    success_count = 0
    fail_count = 0

    # 2. Loop through users and send emails
    for user in users:
        user_id = user.get("id")
        name = user.get("name", "Friend")
        email = user.get("email")
        signup_date = user.get("signup_date")

        if not email:
            print(f"  Skipping user {user_id}: no email")
            continue

        # 3. Calculate day count since signup
        day_count = calculate_day_count(signup_date)

        # 4. Generate the complete message with quote challenge
        message = build_daily_message(name, day_count)

        # 5. Send the email
        print(f"  Sending to {email} (Day {day_count})...", end=" ")
        sent = send_daily_email(email, name, message)

        if sent:
            # 6. Update last_notified_at (Anti-Duplicate Guard)
            update_last_notified(user_id)
            print("OK")
            success_count += 1
        else:
            print("FAILED")
            fail_count += 1

    # Summary
    print(f"\nDispatch complete: {success_count} sent, {fail_count} failed.")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(run_daily_dispatch())
