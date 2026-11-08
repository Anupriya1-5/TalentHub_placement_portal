from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.repositories.repository import ApplicationRepository, CompanyRepository, JobRepository, StudentRepository
from app.schemas.schemas import ApplicationOut, CoordinatorStats
from app.services.serializers import serialize_application

router = APIRouter(prefix="/coordinator", tags=["coordinator"])


@router.get("/stats", response_model=CoordinatorStats)
async def stats(db: AsyncSession = Depends(get_db), _=Depends(require_role("COORDINATOR"))):
    students = await StudentRepository.list_all(db)
    companies = await CompanyRepository.list_all(db)
    jobs = await JobRepository.list_all(db)
    applications = await ApplicationRepository.list_all(db)

    total_offers = sum(1 for a in applications if a.offer is not None)
    total_accepted = sum(1 for a in applications if a.status == "ACCEPTED")
    placed_student_ids = {a.student_id for a in applications if a.status == "ACCEPTED"}
    placement_percentage = (len(placed_student_ids) / len(students) * 100) if students else 0.0

    return CoordinatorStats(
        total_students=len(students),
        total_companies=len(companies),
        total_jobs=len(jobs),
        total_applications=len(applications),
        total_offers=total_offers,
        total_accepted=total_accepted,
        placement_percentage=round(placement_percentage, 1),
    )


@router.get("/applications", response_model=list[ApplicationOut])
async def all_applications(db: AsyncSession = Depends(get_db), _=Depends(require_role("COORDINATOR"))):
    applications = await ApplicationRepository.list_all(db)
    return [serialize_application(a) for a in applications]
