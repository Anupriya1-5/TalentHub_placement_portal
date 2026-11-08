from app.models.models import Application, JobListing
from app.services.eligibility_service import EligibilityService


def serialize_job(job: JobListing, student=None) -> dict:
    data = {
        "id": job.id,
        "company_id": job.company_id,
        "role_title": job.role_title,
        "description": job.description,
        "package_lpa": job.package_lpa,
        "min_cgpa": job.min_cgpa,
        "max_backlogs": job.max_backlogs,
        "company_name": job.company.name if job.company else None,
    }
    if student is not None:
        eligible, reason = EligibilityService.verify_eligibility(student, job)
        data["eligible"] = eligible
        data["reason"] = reason
    return data


def serialize_application(application: Application) -> dict:
    interview = application.interview
    offer = application.offer
    return {
        "id": application.id,
        "student_id": application.student_id,
        "job_id": application.job_id,
        "status": application.status,
        "applied_at": application.applied_at,
        "student_name": application.student.name if application.student else None,
        "student_cgpa": application.student.cgpa if application.student else None,
        "student_backlogs": application.student.active_backlogs if application.student else None,
        "job_title": application.job.role_title if application.job else None,
        "company_name": application.job.company.name if application.job and application.job.company else None,
        "interview": (
            {
                "id": interview.id,
                "scheduled_at": interview.scheduled_at,
                "result": interview.result,
                "notes": interview.notes,
            }
            if interview
            else None
        ),
        "offer": (
            {"id": offer.id, "package_lpa": offer.package_lpa, "status": offer.status, "issued_at": offer.issued_at}
            if offer
            else None
        ),
    }
