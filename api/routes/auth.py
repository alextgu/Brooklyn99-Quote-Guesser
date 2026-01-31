"""
Authentication routes: signup, email confirmation.
Implements the Double Opt-In System.
"""

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from core.database import add_user_to_db, confirm_user
from core.mailer import send_verification_email

router = APIRouter(tags=["auth"])

# Templates directory
TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.post("/signup")
async def handle_signup(request: Request, name: str = Form(...), email: str = Form(...)):
    """
    Handle user enrollment.
    1. Add user to database (confirmed=False)
    2. Send verification email with confirmation link
    """
    # 1. Save to database
    result = add_user_to_db(name, email)

    if not result:
        return templates.TemplateResponse(
            "signup_error.html",
            {
                "request": request,
                "message": "Enrollment failed. This email may already be registered.",
            },
        )

    # 2. Send verification email
    email_sent = send_verification_email(email, name)

    if email_sent:
        return templates.TemplateResponse(
            "signup_success.html",
            {
                "request": request,
                "name": name,
                "email": email,
            },
        )
    else:
        # User saved but email failed
        return templates.TemplateResponse(
            "signup_success.html",
            {
                "request": request,
                "name": name,
                "email": email,
                "warning": "Email could not be sent. Please contact support.",
            },
        )


@router.get("/confirm", response_class=HTMLResponse)
async def handle_confirm(request: Request, email: str):
    """
    Confirm a user's email address.
    Updates confirmed=True in the database.
    """
    result = confirm_user(email)

    if result:
        return templates.TemplateResponse(
            "confirm_success.html",
            {"request": request, "email": email},
        )
    else:
        return templates.TemplateResponse(
            "confirm_error.html",
            {
                "request": request,
                "message": "Confirmation failed. Email not found or already confirmed.",
            },
        )
