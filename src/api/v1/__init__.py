from fastapi import APIRouter

from src.api.v1 import auth, profiles, users

app_router = APIRouter()

app_router.include_router(router=auth.router, prefix="/auth", tags=["auth"])

app_router.include_router(router=users.router, prefix="/user", tags=["users"])
app_router.include_router(router=profiles.router, prefix="/profile", tags=["users"])
