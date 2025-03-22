# Path: routes/__init__.py
from fastapi import APIRouter
from routes.routes import router as rag_model_router

router = APIRouter()

router.include_router(
    rag_model_router,
    prefix="/rag_model"
)
