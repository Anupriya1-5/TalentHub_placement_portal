from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.models.models import JobListing
from app.repositories.repository import JobRepository, StudentRepository
from app.schemas.schemas import JobCreate, JobOut
from app.services.serializers import serialize_job

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobOut])
async def list_jobs(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT", "COORDINATOR", "COMPANY"))):
    jobs = await JobRepository.list_all(db)
    student = None
    if payload["role"] == "STUDENT":
        student = await StudentRepository.get(db, payload["linked_id"])
    return [serialize_job(job, student) for job in jobs]


@router.get("/mine", response_model=list[JobOut])
async def my_jobs(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY"))):
    jobs = await JobRepository.list_by_company(db, payload["linked_id"])
    return [serialize_job(job) for job in jobs]


@router.post("", response_model=JobOut)
async def create_job(
    job_in: JobCreate, db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY"))
):
    job = JobListing(company_id=payload["linked_id"], **job_in.model_dump())
    created = await JobRepository.create(db, job)
    return serialize_job(created)


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db), _=Depends(require_role("STUDENT", "COORDINATOR", "COMPANY"))):
    job = await JobRepository.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return serialize_job(job)
