#!/usr/bin/env python3
"""
The Efficiency Sweep - Purge Unconfirmed Users

Captain Holt does not tolerate incomplete files.
This script deletes unconfirmed users older than 48 hours.

Run manually: python scripts/run_purge.py
Runs automatically via GitHub Actions before daily dispatch.
"""

import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("/", 2)[0])

from core.database import purge_unconfirmed_users
from core.config import settings


def run_purge():
    """
    Execute the Efficiency Sweep.
    Deletes all unconfirmed users older than PURGE_HOURS.
    """
    print(f"[{datetime.utcnow().isoformat()}] Initiating Efficiency Sweep...")
    print(f"Purge threshold: {settings.PURGE_HOURS} hours")

    if not settings.supabase_admin_configured:
        print("ERROR: SUPABASE_SERVICE_KEY not configured. Cannot proceed.")
        return 1

    deleted = purge_unconfirmed_users(hours=settings.PURGE_HOURS)

    if deleted == -1:
        print("ERROR: Purge operation failed.")
        return 1
    elif deleted == 0:
        print("No unconfirmed users to purge. Database is disciplined.")
    else:
        print(f"Purged {deleted} unconfirmed user(s). Order has been restored.")

    return 0


if __name__ == "__main__":
    sys.exit(run_purge())
