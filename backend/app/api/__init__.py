from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.tickets import router as tickets_router
from app.api.knowledge import router as knowledge_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.notices import router as notices_router
from app.api.dashboard import router as dashboard_router
from app.api.users import router as users_router
from app.api.notifications import router as notifications_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(tickets_router)
api_router.include_router(knowledge_router)
api_router.include_router(documents_router)
api_router.include_router(chat_router)
api_router.include_router(notices_router)
api_router.include_router(dashboard_router)
api_router.include_router(users_router)
api_router.include_router(notifications_router)
