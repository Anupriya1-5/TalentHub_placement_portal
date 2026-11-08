from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.models import Application, Company, Interview, JobListing, Offer, Student, User


class UserRepository:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user: User) -> User:
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


class StudentRepository:
    @staticmethod
    async def get(db: AsyncSession, student_id: int) -> Student | None:
        return await db.get(Student, student_id)

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Student]:
        result = await db.execute(select(Student))
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, student: Student) -> Student:
        db.add(student)
        await db.commit()
        await db.refresh(student)
        return student


class CompanyRepository:
    @staticmethod
    async def get(db: AsyncSession, company_id: int) -> Company | None:
        return await db.get(Company, company_id)

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Company]:
        result = await db.execute(select(Company))
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, company: Company) -> Company:
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company


class JobRepository:
    @staticmethod
    async def get(db: AsyncSession, job_id: int) -> JobListing | None:
        result = await db.execute(
            select(JobListing).options(selectinload(JobListing.company)).where(JobListing.id == job_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession) -> list[JobListing]:
        result = await db.execute(select(JobListing).options(selectinload(JobListing.company)))
        return list(result.scalars().all())

    @staticmethod
    async def list_by_company(db: AsyncSession, company_id: int) -> list[JobListing]:
        result = await db.execute(
            select(JobListing).options(selectinload(JobListing.company)).where(JobListing.company_id == company_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, job: JobListing) -> JobListing:
        db.add(job)
        await db.commit()
        await db.refresh(job)
        return await JobRepository.get(db, job.id)


class ApplicationRepository:
    @staticmethod
    async def get(db: AsyncSession, application_id: int) -> Application | None:
        result = await db.execute(
            select(Application)
            .options(
                selectinload(Application.student),
                selectinload(Application.job).selectinload(JobListing.company),
                selectinload(Application.interview),
                selectinload(Application.offer),
            )
            .where(Application.id == application_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_existing(db: AsyncSession, student_id: int, job_id: int) -> Application | None:
        result = await db.execute(
            select(Application).where(Application.student_id == student_id, Application.job_id == job_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_student(db: AsyncSession, student_id: int) -> list[Application]:
        result = await db.execute(
            select(Application)
            .options(
                selectinload(Application.student),
                selectinload(Application.job).selectinload(JobListing.company),
                selectinload(Application.interview),
                selectinload(Application.offer),
            )
            .where(Application.student_id == student_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_by_job(db: AsyncSession, job_id: int) -> list[Application]:
        result = await db.execute(
            select(Application)
            .options(
                selectinload(Application.student),
                selectinload(Application.job).selectinload(JobListing.company),
                selectinload(Application.interview),
                selectinload(Application.offer),
            )
            .where(Application.job_id == job_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_by_company(db: AsyncSession, company_id: int) -> list[Application]:
        result = await db.execute(
            select(Application)
            .join(JobListing, Application.job_id == JobListing.id)
            .options(
                selectinload(Application.student),
                selectinload(Application.job).selectinload(JobListing.company),
                selectinload(Application.interview),
                selectinload(Application.offer),
            )
            .where(JobListing.company_id == company_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Application]:
        result = await db.execute(
            select(Application).options(
                selectinload(Application.student),
                selectinload(Application.job).selectinload(JobListing.company),
                selectinload(Application.interview),
                selectinload(Application.offer),
            )
        )
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, application: Application) -> Application:
        db.add(application)
        await db.commit()
        await db.refresh(application)
        return await ApplicationRepository.get(db, application.id)

    @staticmethod
    async def save(db: AsyncSession, application: Application) -> Application:
        await db.commit()
        await db.refresh(application)
        return await ApplicationRepository.get(db, application.id)


class InterviewRepository:
    @staticmethod
    async def get_by_application(db: AsyncSession, application_id: int) -> Interview | None:
        result = await db.execute(select(Interview).where(Interview.application_id == application_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, interview: Interview) -> Interview:
        db.add(interview)
        await db.commit()
        await db.refresh(interview)
        return interview

    @staticmethod
    async def save(db: AsyncSession, interview: Interview) -> Interview:
        await db.commit()
        await db.refresh(interview)
        return interview


class OfferRepository:
    @staticmethod
    async def get_by_application(db: AsyncSession, application_id: int) -> Offer | None:
        result = await db.execute(select(Offer).where(Offer.application_id == application_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, offer: Offer) -> Offer:
        db.add(offer)
        await db.commit()
        await db.refresh(offer)
        return offer

    @staticmethod
    async def save(db: AsyncSession, offer: Offer) -> Offer:
        await db.commit()
        await db.refresh(offer)
        return offer

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Offer]:
        result = await db.execute(select(Offer))
        return list(result.scalars().all())
