from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.repositories.repository import ApplicationRepository
from app.schemas.schemas import ApplicationOut, InterviewResultRequest, InterviewScheduleRequest
from app.services.placement_service import PlacementService
from app.services.serializers import serialize_application

router = APIRouter(prefix="/interviews", tags=["interviews"])


async def _assert_owns_application(db: AsyncSession, application_id: int, company_id: int):
    application = await ApplicationRepository.get(db, application_id)
    if not application or application.job.company_id != company_id:
        raise HTTPException(status_code=403, detail="Not your job listing")


@router.post("/schedule", response_model=ApplicationOut)
async def schedule_interview(
    body: InterviewScheduleRequest, db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY"))
):
    await _assert_owns_application(db, body.application_id, payload["linked_id"])
    await PlacementService.schedule_interview(db, body.application_id, body.scheduled_at, body.notes)
    application = await ApplicationRepository.get(db, body.application_id)
    return serialize_application(application)


@router.patch("/{application_id}/result", response_model=ApplicationOut)
async def record_result(
    application_id: int,
    body: InterviewResultRequest,
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(require_role("COMPANY")),
):
    await _assert_owns_application(db, application_id, payload["linked_id"])
    await PlacementService.record_interview_result(db, application_id, body.result, body.notes)
    application = await ApplicationRepository.get(db, application_id)
    return serialize_application(application)
