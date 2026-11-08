from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.repositories.repository import ApplicationRepository, JobRepository
from app.schemas.schemas import ApplicationCreate, ApplicationOut, ApplicationStatusUpdate
from app.services.placement_service import PlacementService
from app.services.serializers import serialize_application

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("", response_model=ApplicationOut)
async def apply(
    payload_in: ApplicationCreate, db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))
):
    application = await PlacementService.apply_for_job(db, payload["linked_id"], payload_in.job_id)
    return serialize_application(application)


@router.get("/me", response_model=list[ApplicationOut])
async def my_applications(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))):
    applications = await ApplicationRepository.list_by_student(db, payload["linked_id"])
    return [serialize_application(a) for a in applications]


@router.get("/job/{job_id}", response_model=list[ApplicationOut])
async def applications_for_job(
    job_id: int, db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY", "COORDINATOR"))
):
    if payload["role"] == "COMPANY":
        job = await JobRepository.get(db, job_id)
        if not job or job.company_id != payload["linked_id"]:
            raise HTTPException(status_code=403, detail="Not your job listing")
    applications = await ApplicationRepository.list_by_job(db, job_id)
    return [serialize_application(a) for a in applications]


@router.get("/company/mine", response_model=list[ApplicationOut])
async def my_company_applications(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY"))):
    applications = await ApplicationRepository.list_by_company(db, payload["linked_id"])
    return [serialize_application(a) for a in applications]


@router.patch("/{application_id}/status", response_model=ApplicationOut)
async def update_status(
    application_id: int,
    body: ApplicationStatusUpdate,
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(require_role("COMPANY")),
):
    application = await ApplicationRepository.get(db, application_id)
    if not application or application.job.company_id != payload["linked_id"]:
        raise HTTPException(status_code=403, detail="Not your job listing")
    updated = await PlacementService.update_status(db, application_id, body.status)
    return serialize_application(updated)
