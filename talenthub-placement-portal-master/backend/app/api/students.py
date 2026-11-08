from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.repositories.repository import StudentRepository
from app.schemas.schemas import StudentOut

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentOut])
async def list_students(
    db: AsyncSession = Depends(get_db), _=Depends(require_role("COORDINATOR", "COMPANY"))
):
    return await StudentRepository.list_all(db)


@router.get("/me", response_model=StudentOut)
async def my_profile(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))):
    student = await StudentRepository.get(db, payload["linked_id"])
    if not student:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return student
