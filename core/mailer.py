"""
Email operations for Holt Bot using Kit (ConvertKit).
Handles subscriber management and email sending via Kit API.
"""

import requests
from typing import Optional

from core.config import settings

# Kit API base URL
KIT_API_BASE = "https://api.convertkit.com/v3"


def _kit_request(method: str, endpoint: str, data: dict = None) -> Optional[dict]:
    """Make a request to the Kit API."""
    if not settings.kit_configured:
        print("Kit not configured: KIT_API_KEY missing")
        return None
    
    url = f"{KIT_API_BASE}/{endpoint}"
    params = {"api_secret": settings.KIT_API_SECRET} if settings.KIT_API_SECRET else {"api_key": settings.KIT_API_KEY}
    
    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=30)
        elif method == "POST":
            if data:
                data.update(params)
            else:
                data = params
            response = requests.post(url, json=data, timeout=30)
        else:
            return None
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Kit API Error: {e}")
        return None


def add_subscriber_to_kit(email: str, name: str) -> bool:
    """
    Add a subscriber to Kit.
    They'll receive a confirmation email from Kit if double opt-in is enabled.
    
    Returns True if successful.
    """
    if not settings.kit_configured:
        print("Kit not configured")
        return False
    
    data = {
        "api_key": settings.KIT_API_KEY,
        "email": email,
        "first_name": name,
    }
    
    # Add to Kit (you can specify a form_id or tag_id for segmentation)
    # For now, just add as a subscriber
    result = _kit_request("POST", "subscribers", data)
    
    if result and result.get("subscription"):
        print(f"Added {email} to Kit")
        return True
    
    print(f"Failed to add {email} to Kit: {result}")
    return False


def send_verification_email(email: str, name: str) -> bool:
    """
    For Kit, we add the subscriber and Kit handles the confirmation.
    Kit's double opt-in feature sends the verification automatically.
    
    Returns True if subscriber was added successfully.
    """
    return add_subscriber_to_kit(email, name)


def send_daily_email(
    email: str, 
    name: str, 
    message: str,
    quote_text: str = None,
    current_streak: int = 0,
    best_streak: int = 0,
) -> bool:
    """
    Send a daily email to a specific subscriber.
    
    Note: Kit is designed for broadcasts (same email to all subscribers).
    For individual personalized emails, we use their subscriber endpoint
    or you can create a broadcast in Kit's dashboard and trigger it.
    
    For now, this creates a broadcast with personalization tags.
    """
    if not settings.kit_configured:
        print("Kit not configured: KIT_API_KEY missing")
        return False
    
    # Convert newlines to HTML breaks
    html_message = message.replace("\n", "<br>")
    
    # URLs
    gif_url = f"{settings.BASE_URL}/static/holt.gif"
    game_url = f"{settings.BASE_URL}/game"
    
    # Build quote section if provided
    quote_section = ""
    if quote_text:
        quote_section = f"""
            <div style="background: #1a1a2e; color: #fff; padding: 20px; border-radius: 8px; margin-top: 30px;">
                <h3 style="margin: 0 0 15px 0; color: #f4c542; font-size: 18px;">📺 TODAY'S CHALLENGE: Who Said It?</h3>
                
                <p style="font-style: italic; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                    "{quote_text}"
                </p>
                
                <a href="{game_url}" style="display: inline-block; background: #f4c542; color: #1a1a2e; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px;">
                    PLAY NOW →
                </a>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <span style="display: inline-block; padding: 10px 20px; margin: 0 10px;">
                    <div style="font-size: 24px; font-weight: bold; color: #f4c542;">🔥 {current_streak}</div>
                    <div style="font-size: 12px; color: #666;">Current Streak</div>
                </span>
                <span style="display: inline-block; padding: 10px 20px; margin: 0 10px;">
                    <div style="font-size: 24px; font-weight: bold; color: #1a5f7a;">⭐ {best_streak}</div>
                    <div style="font-size: 12px; color: #666;">Best Streak</div>
                </span>
            </div>
        """
    
    email_html = f"""
        <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333; line-height: 1.8;">
            
            <div style="white-space: pre-line; font-size: 16px;">
                {html_message}
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <img src="{gif_url}" alt="Captain Holt" style="max-width: 100%; border-radius: 8px;">
            </div>
            
            {quote_section}
            
            <hr style="border: none; border-top: 1px solid #ccc; margin: 30px 0;">
            <p style="font-size: 12px; color: #888;">
                You are receiving this because you signed up for Holt daily dispatches.
            </p>
        </div>
    """
    
    # Kit Broadcast API
    # Note: Broadcasts send to ALL subscribers or a segment
    # For true per-user emails, you'd need Kit's automation or a different approach
    
    broadcast_data = {
        "api_secret": settings.KIT_API_SECRET,
        "subject": f"Your Daily Dispatch, {name}",
        "content": email_html,
        "email_layout_template": "Text Only",  # Use minimal template
        "public": False,
    }
    
    try:
        url = f"{KIT_API_BASE}/broadcasts"
        response = requests.post(url, json=broadcast_data, timeout=30)
        
        if response.status_code in [200, 201]:
            broadcast = response.json().get("broadcast", {})
            broadcast_id = broadcast.get("id")
            
            # Broadcasts need to be manually sent or scheduled
            # Auto-send it
            if broadcast_id:
                send_url = f"{KIT_API_BASE}/broadcasts/{broadcast_id}/send"
                send_response = requests.post(send_url, json={"api_secret": settings.KIT_API_SECRET}, timeout=30)
                if send_response.status_code in [200, 201]:
                    return True
            
            return True
        else:
            print(f"Kit Broadcast Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"Kit API Error: {e}")
        return False
