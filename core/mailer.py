"""
Email operations for Holt Bot.
Handles all Resend API interactions for sending emails.
"""

from core.config import settings

# Initialize Resend client
resend = None
if settings.resend_configured:
    try:
        import resend as resend_lib
        resend_lib.api_key = settings.RESEND_API_KEY
        resend = resend_lib
    except Exception:
        resend = None


def send_verification_email(email: str, name: str) -> bool:
    """
    Sends a verification email to the user with a confirmation link.
    Returns True if sent successfully, False otherwise.
    """
    if resend is None:
        print("Mailer not configured: RESEND_API_KEY missing or invalid")
        return False

    if not settings.BASE_URL:
        print("Mailer not configured: BASE_URL missing")
        return False

    confirmation_link = f"{settings.BASE_URL}/confirm?email={email}"

    try:
        params = {
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": "Please Confirm Your Email Address",
            "html": f"""
                <h1>Welcome, {name}!</h1>
                <p>Thank you for signing up. Please confirm your email address by clicking the link below:</p>
                <p><a href="{confirmation_link}">Confirm My Email</a></p>
                <p>If you did not sign up for this service, please ignore this email.</p>
                <br>
                <p>Best regards,<br>The Holt Team</p>
            """,
        }
        response = resend.Emails.send(params)
        return response is not None
    except Exception as e:
        print(f"Email Error: {e}")
        return False


def send_daily_email(
    email: str, 
    name: str, 
    message: str,
    quote_text: str = None,
    current_streak: int = 0,
    best_streak: int = 0,
) -> bool:
    """
    Sends the daily Holt message to a user.
    Includes the motivational message, daily quote game, and user stats.
    
    Args:
        email: Recipient email address
        name: User's name
        message: The generated Holt message
        quote_text: The masked daily quote for the game
        current_streak: User's current streak
        best_streak: User's best streak ever
        
    Returns:
        True if sent successfully, False otherwise
    """
    if resend is None:
        print("Mailer not configured: RESEND_API_KEY missing or invalid")
        return False

    # Convert newlines to HTML breaks for proper formatting
    html_message = message.replace("\n", "<br>")
    
    # URLs
    gif_url = f"{settings.BASE_URL}/static/holt.gif"
    game_url = f"{settings.BASE_URL}/game"
    
    # Build quote section if provided
    quote_section = ""
    if quote_text:
        quote_section = f"""
            <!-- Daily Quote Game -->
            <div style="background: #1a1a2e; color: #fff; padding: 20px; border-radius: 8px; margin-top: 30px;">
                <h3 style="margin: 0 0 15px 0; color: #f4c542; font-size: 18px;">📺 TODAY'S CHALLENGE: Who Said It?</h3>
                
                <p style="font-style: italic; font-size: 16px; line-height: 1.6; margin: 0 0 20px 0;">
                    "{quote_text}"
                </p>
                
                <a href="{game_url}" style="display: inline-block; background: #f4c542; color: #1a1a2e; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 6px;">
                    PLAY NOW →
                </a>
            </div>
            
            <!-- User Stats -->
            <div style="display: flex; justify-content: center; gap: 30px; margin-top: 20px; text-align: center;">
                <div style="display: inline-block; padding: 10px 20px;">
                    <div style="font-size: 24px; font-weight: bold; color: #f4c542;">🔥 {current_streak}</div>
                    <div style="font-size: 12px; color: #666;">Current Streak</div>
                </div>
                <div style="display: inline-block; padding: 10px 20px;">
                    <div style="font-size: 24px; font-weight: bold; color: #1a5f7a;">⭐ {best_streak}</div>
                    <div style="font-size: 12px; color: #666;">Best Streak</div>
                </div>
            </div>
        """

    try:
        params = {
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": f"Your Daily Dispatch, {name}",
            "html": f"""
                <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333; line-height: 1.8;">
                    
                    <!-- Message Content -->
                    <div style="white-space: pre-line; font-size: 16px;">
                        {html_message}
                    </div>
                    
                    <!-- GIF -->
                    <div style="text-align: center; margin-top: 30px;">
                        <img src="{gif_url}" alt="Captain Holt" style="max-width: 100%; border-radius: 8px;">
                    </div>
                    
                    {quote_section}
                    
                    <hr style="border: none; border-top: 1px solid #ccc; margin: 30px 0;">
                    <p style="font-size: 12px; color: #888;">
                        You are receiving this because you signed up for Holt daily dispatches.
                    </p>
                </div>
            """,
        }
        response = resend.Emails.send(params)
        return response is not None
    except Exception as e:
        print(f"Email Error: {e}")
        return False
