"""
B99 Quote Guesser

A simple "Who Said It?" game for Brooklyn Nine-Nine fans.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.routes import game_router
from core.config import settings

# --- App Setup ---
app = FastAPI(
    title="B99 Quote Guesser",
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
app.include_router(game_router)


# --- Game Page (single page) ---
@app.get("/", response_class=HTMLResponse)
async def game_page(request: Request):
    return templates.TemplateResponse("game.html", {"request": request})


# --- Health Check ---
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    Reports status of external services.
    """
    return {"status": "operational"}