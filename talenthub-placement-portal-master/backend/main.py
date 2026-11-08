from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import applications, auth, companies, coordinator, interviews, jobs, offers, students, career_tools
from app.core.database import AsyncSessionLocal, init_db
from app.seed import seed_if_empty

app = FastAPI(title="TalentHub Placement Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_if_empty(db)


@app.get("/")
def read_root():
    return {"message": "Welcome to TalentHub Campus Placement Management API"}


app.include_router(auth.router)
app.include_router(students.router)
app.include_router(companies.router)
app.include_router(jobs.router)
app.include_router(applications.router)
app.include_router(interviews.router)
app.include_router(offers.router)
app.include_router(coordinator.router)
app.include_router(career_tools.router)
