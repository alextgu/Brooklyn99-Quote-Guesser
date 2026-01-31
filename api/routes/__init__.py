"""
API Route modules for Holt Bot.
"""

from api.routes.auth import router as auth_router
from api.routes.game import router as game_router

__all__ = ["auth_router", "game_router"]
