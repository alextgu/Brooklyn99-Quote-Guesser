"""
Holt Bot - Main FastAPI Application

Features:
- Minimalist Landing Page (Tailwind CSS)
- Double Opt-In System (Resend API)
- "Who Said It?" Game (B99 API)
- Daily Dispatch Engine (CRON)
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routes import auth_router, game_router
from core.config import settings

# --- App Setup ---
app = FastAPI(
    title="Holt Bot",
    description="Captain Dad will encourage you to be happy",
    version="1.0.0",
)

# --- Path Configuration ---
BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# --- Static Files ---
if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# --- Templates ---
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# --- Include Routers ---
app.include_router(auth_router)
app.include_router(game_router)


# --- Landing Page ---
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """
    Minimalist Landing Page: A formal, high-efficiency UI for user enrollment.
    """
    return templates.TemplateResponse("index.html", {"request": request})


# --- Personalized Holt Image ---
@app.get("/holt/{name}", response_class=HTMLResponse)
async def holt_image(request: Request, name: str):
    """
    Dynamic page showing Holt GIF with personalized name overlay.
    Used in emails: {BASE_URL}/holt/Rosa → Shows GIF with "Rosa" overlaid
    """
    return templates.TemplateResponse("holt_image.html", {
        "request": request,
        "name": name,
    })


# --- Health Check ---
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Reports status of external services.
    """
    return {
        "status": "operational",
        "services": {
            "supabase": settings.supabase_configured,
            "supabase_admin": settings.supabase_admin_configured,
            "kit": settings.kit_configured,
        },
    }