from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # STUDENT, COMPANY, COORDINATOR
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    branch = Column(String)
    cgpa = Column(Float)
    active_backlogs = Column(Integer, default=0)

    applications = relationship("Application", back_populates="student")


class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, default="")

    jobs = relationship("JobListing", back_populates="company")


class JobListing(Base):
    __tablename__ = "job_listings"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    role_title = Column(String, nullable=False)
    description = Column(String, default="")
    package_lpa = Column(Float, default=0.0)
    min_cgpa = Column(Float, default=0.0)
    max_backlogs = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="jobs")
    applications = relationship("Application", back_populates="job")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    job_id = Column(Integer, ForeignKey("job_listings.id"))
    # APPLIED, SHORTLISTED, REJECTED, INTERVIEW_SCHEDULED, OFFERED, ACCEPTED, DECLINED
    status = Column(String, default="APPLIED")
    applied_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="applications")
    job = relationship("JobListing", back_populates="applications")
    interview = relationship("Interview", back_populates="application", uselist=False)
    offer = relationship("Offer", back_populates="application", uselist=False)


class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True)
    scheduled_at = Column(DateTime, nullable=False)
    result = Column(String, default="PENDING")  # PENDING, PASS, FAIL
    notes = Column(String, default="")

    application = relationship("Application", back_populates="interview")


class Offer(Base):
    __tablename__ = "offers"
    id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer, ForeignKey("applications.id"), unique=True)
    package_lpa = Column(Float, default=0.0)
    status = Column(String, default="ISSUED")  # ISSUED, ACCEPTED, DECLINED
    issued_at = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="offer")


class StudentSkillProfile(Base):
    __tablename__ = "student_skill_profiles"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True, nullable=False)
    skills = Column(Text, default="[]", nullable=False)
    resume_filename = Column(String, default="")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
