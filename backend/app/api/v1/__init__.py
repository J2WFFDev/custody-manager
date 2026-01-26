from fastapi import APIRouter
from app.api.v1.endpoints import kits

api_router = APIRouter()

# Include routers
api_router.include_router(kits.router)

@api_router.get("/")
async def api_root():
    return {"message": "API v1"}
