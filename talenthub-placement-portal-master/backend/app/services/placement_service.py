from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Application, Interview, JobListing, Offer
from app.repositories.repository import (
    ApplicationRepository,
    InterviewRepository,
    JobRepository,
    OfferRepository,
    StudentRepository,
)
from app.services.eligibility_service import EligibilityService


class PlacementService:
    @staticmethod
    async def apply_for_job(db: AsyncSession, student_id: int, job_id: int) -> Application:
        student = await StudentRepository.get(db, student_id)
        job = await JobRepository.get(db, job_id)
        if not student or not job:
            raise HTTPException(status_code=404, detail="Student or Job Listing not found")

        existing = await ApplicationRepository.get_existing(db, student_id, job_id)
        if existing:
            raise HTTPException(status_code=400, detail="You have already applied to this job")

        is_eligible, reason = EligibilityService.verify_eligibility(student, job)
        if not is_eligible:
            raise HTTPException(status_code=400, detail=f"Application Rejected: {reason}")

        application = Application(student_id=student_id, job_id=job_id, status="APPLIED")
        return await ApplicationRepository.create(db, application)

    @staticmethod
    async def update_status(db: AsyncSession, application_id: int, status: str) -> Application:
        application = await ApplicationRepository.get(db, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")
        if status not in ("SHORTLISTED", "REJECTED"):
            raise HTTPException(status_code=400, detail="Invalid status")
        application.status = status
        return await ApplicationRepository.save(db, application)

    @staticmethod
    async def schedule_interview(db: AsyncSession, application_id: int, scheduled_at, notes: str) -> Interview:
        application = await ApplicationRepository.get(db, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        existing = await InterviewRepository.get_by_application(db, application_id)
        if existing:
            existing.scheduled_at = scheduled_at
            existing.notes = notes
            interview = await InterviewRepository.save(db, existing)
        else:
            interview = await InterviewRepository.create(
                db, Interview(application_id=application_id, scheduled_at=scheduled_at, notes=notes)
            )

        application.status = "INTERVIEW_SCHEDULED"
        await ApplicationRepository.save(db, application)
        return interview

    @staticmethod
    async def record_interview_result(db: AsyncSession, application_id: int, result: str, notes: str) -> Interview:
        interview = await InterviewRepository.get_by_application(db, application_id)
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not scheduled yet")
        if result not in ("PASS", "FAIL"):
            raise HTTPException(status_code=400, detail="Invalid result")
        interview.result = result
        interview.notes = notes or interview.notes
        return await InterviewRepository.save(db, interview)

    @staticmethod
    async def issue_offer(db: AsyncSession, application_id: int, package_lpa: float) -> Offer:
        application = await ApplicationRepository.get(db, application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        existing = await OfferRepository.get_by_application(db, application_id)
        if existing:
            raise HTTPException(status_code=400, detail="Offer already issued for this application")

        offer = await OfferRepository.create(
            db, Offer(application_id=application_id, package_lpa=package_lpa, status="ISSUED")
        )
        application.status = "OFFERED"
        await ApplicationRepository.save(db, application)
        return offer

    @staticmethod
    async def respond_to_offer(db: AsyncSession, application_id: int, student_id: int, accept: bool) -> Offer:
        application = await ApplicationRepository.get(db, application_id)
        if not application or application.student_id != student_id:
            raise HTTPException(status_code=404, detail="Application not found")

        offer = await OfferRepository.get_by_application(db, application_id)
        if not offer:
            raise HTTPException(status_code=404, detail="No offer found for this application")

        offer.status = "ACCEPTED" if accept else "DECLINED"
        application.status = "ACCEPTED" if accept else "DECLINED"
        await ApplicationRepository.save(db, application)
        return await OfferRepository.save(db, offer)
