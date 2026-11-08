from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str
    linked_id: Optional[int] = None


class StudentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: str
    branch: str
    cgpa: float
    active_backlogs: int


class CompanyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str


class JobCreate(BaseModel):
    role_title: str
    description: str = ""
    package_lpa: float = 0.0
    min_cgpa: float = 0.0
    max_backlogs: int = 0


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_id: int
    role_title: str
    description: str
    package_lpa: float
    min_cgpa: float
    max_backlogs: int
    company_name: Optional[str] = None
    eligible: Optional[bool] = None
    reason: Optional[str] = None


class ApplicationCreate(BaseModel):
    job_id: int


class InterviewScheduleRequest(BaseModel):
    application_id: int
    scheduled_at: datetime
    notes: str = ""


class InterviewResultRequest(BaseModel):
    result: str  # PASS / FAIL
    notes: str = ""


class OfferCreate(BaseModel):
    application_id: int
    package_lpa: float


class OfferRespondRequest(BaseModel):
    accept: bool


class ApplicationStatusUpdate(BaseModel):
    status: str  # SHORTLISTED / REJECTED


class ApplicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    student_id: int
    job_id: int
    status: str
    applied_at: datetime
    student_name: Optional[str] = None
    student_cgpa: Optional[float] = None
    student_backlogs: Optional[int] = None
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    interview: Optional[dict] = None
    offer: Optional[dict] = None


class CoordinatorStats(BaseModel):
    total_students: int
    total_companies: int
    total_jobs: int
    total_applications: int
    total_offers: int
    total_accepted: int
    placement_percentage: float
