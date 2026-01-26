from fastapi import APIRouter
from app.api.v1.endpoints import kits

api_router = APIRouter()

# Include endpoint routers
api_router.include_router(kits.router, prefix="/kits", tags=["kits"])
from app.api.v1.endpoints import auth

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

@api_router.get("/")
async def api_root():
    return {"message": "API v1"}
