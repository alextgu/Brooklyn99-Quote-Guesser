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

    # 2. Fetch TODAY'S universal quote (same for all users)
    daily_quote = get_random_quote_sync()
    if daily_quote:
        print(f"Today's quote: \"{daily_quote.text[:50]}...\" - {daily_quote.character}")
    else:
        print("Warning: Could not fetch daily quote")

    success_count = 0
    fail_count = 0

    # 3. Loop through users and send emails
    for user in users:
        user_id = user.get("id")
        name = user.get("name", "Friend")
        email = user.get("email")
        signup_date = user.get("signup_date")
        current_streak = user.get("current_streak", 0) or 0
        best_streak = user.get("best_streak", 0) or 0

        if not email:
            print(f"  Skipping user {user_id}: no email")
            continue

        # 4. Calculate day count since signup
        day_count = calculate_day_count(signup_date)

        # 5. Generate the Holt message (affirmations only)
        holt_message = generate_holt_message(name, day_count)

        # 6. Send the email with quote and stats
        print(f"  Sending to {email} (Day {day_count}, Streak: {current_streak})...", end=" ")
        sent = send_daily_email(
            email=email,
            name=name,
            message=holt_message,
            quote_text=daily_quote.masked_text() if daily_quote else None,
            current_streak=current_streak,
            best_streak=best_streak,
        )

        if sent:
            # 7. Update last_notified_at (Anti-Duplicate Guard)
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
