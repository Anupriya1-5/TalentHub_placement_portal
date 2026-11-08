from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_token_payload
from app.repositories.repository import UserRepository
from app.schemas.schemas import LoginRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await AuthService.login(db, payload.email, payload.password)


@router.get("/me")
async def me(token_payload: dict = Depends(get_token_payload), db: AsyncSession = Depends(get_db)):
    return {
        "role": token_payload.get("role"),
        "linked_id": token_payload.get("linked_id"),
        "user_id": int(token_payload.get("sub")),
    }
