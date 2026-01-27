from fastapi import APIRouter

from app.api.v1.endpoints import auth, kits, users, custody

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include kits routes
api_router.include_router(kits.router, prefix="/kits", tags=["kits"])

# Include users routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include custody routes
api_router.include_router(custody.router, prefix="/custody", tags=["custody"])

@api_router.get("/")
async def api_root():
    return {"message": "API v1"}

