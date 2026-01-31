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


def send_daily_email(email: str, name: str, message: str) -> bool:
    """
    Sends the daily Holt message to a user.
    Simple, text-heavy HTML email containing the generated message.
    
    Args:
        email: Recipient email address
        name: User's name
        message: The generated Holt message
        
    Returns:
        True if sent successfully, False otherwise
    """
    if resend is None:
        print("Mailer not configured: RESEND_API_KEY missing or invalid")
        return False

    # Convert newlines to HTML breaks for proper formatting
    html_message = message.replace("\n", "<br>")

    try:
        params = {
            "from": settings.EMAIL_FROM,
            "to": [email],
            "subject": f"Your Daily Dispatch, {name}",
            "html": f"""
                <div style="font-family: Georgia, serif; max-width: 600px; margin: 0 auto; padding: 20px; color: #333; line-height: 1.8;">
                    <div style="white-space: pre-line; font-size: 16px;">
                        {html_message}
                    </div>
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
