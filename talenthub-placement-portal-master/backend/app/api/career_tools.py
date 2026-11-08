import json
import re
from collections import Counter
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import require_role
from app.models.models import StudentSkillProfile, Student, JobListing, Application, Interview, Company
from app.repositories.repository import ApplicationRepository, JobRepository, StudentRepository
from pypdf import PdfReader
from io import BytesIO

router = APIRouter(tags=["TalentHub 2.0 - Career Tools"])
SKILL_TERMS = [
    "python", "java", "javascript", "typescript", "c", "c++", "sql", "html", "css", "react", "node.js", "fastapi", "django", "flask", "machine learning", "deep learning", "artificial intelligence", "data science", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch", "opencv", "nlp", "computer vision", "aws", "azure", "docker", "kubernetes", "git", "linux", "mongodb", "postgresql", "mysql", "rest api", "communication", " problem solving", "excel", "power bi", "tableau", "figma", "testing", "selenium", "agile"
]

def extract_skills(text: str):
    normalized = re.sub(r"\s+", " ", text.lower())
    found = []
    for skill in SKILL_TERMS:
        term = skill.strip()
        if term and re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", normalized):
            found.append(term.title() if term not in {"c", "c++", "sql", "nlp", "aws", "html", "css", "git", "linux"} else term.upper())
    return sorted(set(found))

async def get_profile(db, student_id):
    result = await db.execute(select(StudentSkillProfile).where(StudentSkillProfile.student_id == student_id))
    return result.scalars().first()

@router.post("/students/me/resume")
async def upload_resume(file: UploadFile = File(...), db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Please upload a PDF resume.")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Resume must be 5 MB or smaller.")
    try:
        reader = PdfReader(BytesIO(data))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read this PDF. Please upload a text-based PDF.")
    if not text.strip():
        raise HTTPException(status_code=400, detail="No selectable text found. Please upload a text-based PDF.")
    skills = extract_skills(text)
    profile = await get_profile(db, payload["linked_id"])
    if profile:
        profile.skills = json.dumps(skills)
        profile.resume_filename = file.filename
    else:
        db.add(StudentSkillProfile(student_id=payload["linked_id"], skills=json.dumps(skills), resume_filename=file.filename))
    await db.commit()
    return {"filename": file.filename, "skills": skills, "skill_count": len(skills), "message": "Resume analyzed successfully."}

@router.get("/students/me/skills")
async def my_skills(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))):
    profile = await get_profile(db, payload["linked_id"])
    return {"skills": json.loads(profile.skills) if profile else [], "resume_filename": profile.resume_filename if profile else None}

@router.get("/students/me/recommendations")
async def recommendations(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))):
    student = await StudentRepository.get(db, payload["linked_id"])
    jobs = await JobRepository.list_all(db)
    profile = await get_profile(db, payload["linked_id"])
    skills = set(json.loads(profile.skills)) if profile else set()
    result = []
    for job in jobs:
        required = set(extract_skills(f"{job.role_title} {job.description}"))
        matched = sorted(skills & required)
        missing = sorted(required - skills)
        score = round((len(matched) / len(required)) * 100) if required else 0
        eligible = student.cgpa >= job.min_cgpa and student.active_backlogs <= job.max_backlogs
        result.append({"job_id": job.id, "role_title": job.role_title, "company_name": job.company.name if job.company else "", "package_lpa": job.package_lpa, "eligible": eligible, "match_score": score, "matched_skills": matched, "missing_skills": missing})
    return sorted(result, key=lambda x: (x["eligible"], x["match_score"]), reverse=True)

@router.get("/students/me/skill-gap/{job_id}")
async def skill_gap(job_id: int, db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("STUDENT"))):
    job = await JobRepository.get(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    profile = await get_profile(db, payload["linked_id"])
    have = set(json.loads(profile.skills)) if profile else set()
    required = set(extract_skills(f"{job.role_title} {job.description}"))
    return {"job_id": job.id, "role_title": job.role_title, "your_skills": sorted(have & required), "missing_skills": sorted(required - have), "required_skills": sorted(required)}

@router.get("/coordinator/analytics")
async def placement_analytics(db: AsyncSession = Depends(get_db), _=Depends(require_role("COORDINATOR"))):
    students = (await db.execute(select(Student))).scalars().all()
    jobs = (await db.execute(select(JobListing))).scalars().all()
    apps = (await db.execute(select(Application))).scalars().all()
    interviews = (await db.execute(select(Interview))).scalars().all()
    status_counts = Counter(a.status for a in apps)
    company_rows = await db.execute(select(Company.name, Application.id).join(JobListing, JobListing.company_id == Company.id).join(Application, Application.job_id == JobListing.id))
    company_counts = Counter(row[0] for row in company_rows.all())
    return {"total_students": len(students), "total_jobs": len(jobs), "total_applications": len(apps), "total_interviews": len(interviews), "status_counts": dict(status_counts), "company_applications": dict(company_counts), "placement_percentage": round(len({a.student_id for a in apps if a.status == "ACCEPTED"}) / len(students) * 100, 1) if students else 0}

@router.get("/interviews/calendar")
async def interview_calendar(db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY", "COORDINATOR", "STUDENT"))):
    statement = select(Interview).join(Application).join(JobListing).join(Company).options(
        selectinload(Interview.application).selectinload(Application.student),
        selectinload(Interview.application).selectinload(Application.job).selectinload(JobListing.company),
    )
    result = await db.execute(statement)
    interviews = result.scalars().all()
    if payload["role"] == "COMPANY":
        interviews = [i for i in interviews if i.application.job.company_id == payload["linked_id"]]
    elif payload["role"] == "STUDENT":
        interviews = [i for i in interviews if i.application.student_id == payload["linked_id"]]
    return [{"id": i.id, "application_id": i.application_id, "scheduled_at": i.scheduled_at.isoformat(), "result": i.result, "notes": i.notes, "student_name": i.application.student.name, "company_name": i.application.job.company.name, "role_title": i.application.job.role_title} for i in sorted(interviews, key=lambda x: x.scheduled_at)]
