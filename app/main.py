from fastapi import FastAPI
from app.routes import router
from src.config import settings

api = FastAPI(title=settings.service_name, version=settings.service_version)
api.include_router(router)

