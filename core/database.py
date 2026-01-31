"""
Database operations for Holt Bot.
Handles all Supabase interactions for user management.
"""

from datetime import date, datetime, timedelta
from core.config import settings

# Initialize Supabase clients
supabase = None
supabase_admin = None

if settings.supabase_configured:
    try:
        from supabase import create_client
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    except Exception:
        supabase = None

# Admin client uses service key to bypass RLS
if settings.supabase_admin_configured:
    try:
        from supabase import create_client
        supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    except Exception:
        supabase_admin = None


def add_user_to_db(name: str, email: str):
    """
    Takes user info and saves it to the 'users' table in Supabase.
    """
    if supabase is None:
        return None
    try:
        data = {
            "name": name, 
            "email": email, 
            "confirmed": False  # New users start unconfirmed
        }
        # .table("users") targets the table you created
        # .insert(data) adds the new row
        # .execute() tells Supabase to perform the action
        response = supabase.table("users").insert(data).execute()
        return response
    except Exception as e:
        print(f"Database Error: {e}")
        return None


def confirm_user(email: str):
    """
    Updates the user's confirmed status to True in the 'users' table.
    Returns the response if successful, None otherwise.
    """
    if supabase is None:
        return None
    try:
        response = (
            supabase.table("users")
            .update({"confirmed": True})
            .eq("email", email)
            .execute()
        )
        # Check if any rows were updated
        if response.data and len(response.data) > 0:
            return response
        return None
    except Exception as e:
        print(f"Database Error: {e}")
        return None


def get_confirmed_users_for_dispatch(today: date | None = None):
    """
    Fetches all confirmed users who haven't been notified today.
    Uses the admin client (service key) to bypass RLS.
    
    Args:
        today: The current date (defaults to today if not provided)
        
    Returns:
        List of user dicts with id, name, email, signup_date, last_notified_at
        Returns empty list on error.
    """
    if supabase_admin is None:
        print("Admin client not configured: SUPABASE_SERVICE_KEY missing")
        return []
    
    if today is None:
        today = date.today()
    
    today_str = today.isoformat()
    
    try:
        # Fetch confirmed users
        response = (
            supabase_admin.table("users")
            .select("id, name, email, signup_date, last_notified_at")
            .eq("confirmed", True)
            .execute()
        )
        
        if not response.data:
            return []
        
        # Filter out users already notified today
        users_to_notify = []
        for user in response.data:
            last_notified = user.get("last_notified_at")
            if last_notified:
                # Parse the timestamp and check if it's today
                last_date = last_notified[:10]  # Extract YYYY-MM-DD
                if last_date == today_str:
                    continue  # Skip - already notified today
            users_to_notify.append(user)
        
        return users_to_notify
    except Exception as e:
        print(f"Database Error: {e}")
        return []


def update_last_notified(user_id: int) -> bool:
    """
    Updates the last_notified_at timestamp for a user.
    Uses the admin client (service key) to bypass RLS.
    
    Args:
        user_id: The user's ID
        
    Returns:
        True if updated successfully, False otherwise
    """
    if supabase_admin is None:
        print("Admin client not configured: SUPABASE_SERVICE_KEY missing")
        return False
    
    try:
        response = (
            supabase_admin.table("users")
            .update({"last_notified_at": datetime.utcnow().isoformat()})
            .eq("id", user_id)
            .execute()
        )
        return response.data and len(response.data) > 0
    except Exception as e:
        print(f"Database Error: {e}")
        return False


def calculate_day_count(signup_date_str: str | None) -> int:
    """
    Calculates the number of days since signup.
    
    Args:
        signup_date_str: ISO format date string (YYYY-MM-DD or timestamp)
        
    Returns:
        Number of days since signup, minimum 1
    """
    if not signup_date_str:
        return 1
    
    try:
        # Handle both date and timestamp formats
        signup_date = date.fromisoformat(signup_date_str[:10])
        delta = date.today() - signup_date
        return max(1, delta.days + 1)  # Day 1 on signup day
    except (ValueError, TypeError):
        return 1


def purge_unconfirmed_users(hours: int = 48) -> int:
    """
    Deletes users where confirmed=False and signup_date is older than the specified hours.
    Captain Holt does not tolerate incomplete files.
    
    Uses the admin client (service key) to bypass RLS.
    
    Args:
        hours: Number of hours after which unconfirmed users are deleted (default 48)
        
    Returns:
        Number of users deleted, or -1 on error
    """
    if supabase_admin is None:
        print("Admin client not configured: SUPABASE_SERVICE_KEY missing")
        return -1
    
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    cutoff_str = cutoff.isoformat()
    
    try:
        # Delete unconfirmed users older than cutoff
        response = (
            supabase_admin.table("users")
            .delete()
            .eq("confirmed", False)
            .lt("signup_date", cutoff_str)
            .execute()
        )
        
        deleted_count = len(response.data) if response.data else 0
        if deleted_count > 0:
            print(f"Purged {deleted_count} unconfirmed user(s) older than {hours} hours.")
        return deleted_count
    except Exception as e:
        print(f"Database Error during purge: {e}")
        return -1