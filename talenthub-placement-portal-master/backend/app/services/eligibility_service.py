from app.models.models import JobListing, Student


class EligibilityService:
    @staticmethod
    def verify_eligibility(student: Student, job: JobListing) -> tuple[bool, str]:
        """Core business logic rule checking (TalentHub SRS Spec)"""
        if student.cgpa < job.min_cgpa:
            return False, f"CGPA ({student.cgpa}) is below required minimum ({job.min_cgpa})"
        if student.active_backlogs > job.max_backlogs:
            return False, f"Active backlogs ({student.active_backlogs}) exceed maximum allowed ({job.max_backlogs})"
        return True, "Eligible to apply"
