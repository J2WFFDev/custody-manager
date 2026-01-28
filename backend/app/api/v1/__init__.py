from fastapi import APIRouter

from app.api.v1.endpoints import auth, kits, items, users, custody, events, maintenance

api_router = APIRouter()

# Include auth routes
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

# Include kits routes
api_router.include_router(kits.router, prefix="/kits", tags=["kits"])

# Include items routes (master inventory)
api_router.include_router(items.router, prefix="/items", tags=["items"])

# Include users routes
api_router.include_router(users.router, prefix="/users", tags=["users"])

# Include custody routes
api_router.include_router(custody.router, prefix="/custody", tags=["custody"])

# Include events routes
api_router.include_router(events.router, prefix="/events", tags=["events"])
# Include maintenance routes
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])

@api_router.get("/")
async def api_root():
    return {"message": "API v1"}

