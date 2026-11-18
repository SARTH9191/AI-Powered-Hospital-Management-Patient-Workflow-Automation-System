"""
API Package - FastAPI Routers
Exposes all 110+ hospital management tools through AI Chat Router
"""

# Import available routers
from api.ai_chat_router import router as ai_chat_router

__all__ = [
    "ai_chat_router"
]

# Note: All hospital management functionality (110+ tools) is accessible 
# through the ai_chat_router which provides a comprehensive conversational
# interface for the complete hospital workflow (Stages 1-11)
