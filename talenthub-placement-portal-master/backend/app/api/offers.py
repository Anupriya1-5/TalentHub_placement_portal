from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_role
from app.repositories.repository import ApplicationRepository
from app.schemas.schemas import ApplicationOut, OfferCreate, OfferRespondRequest
from app.services.placement_service import PlacementService
from app.services.serializers import serialize_application

router = APIRouter(prefix="/offers", tags=["offers"])


@router.post("", response_model=ApplicationOut)
async def issue_offer(
    body: OfferCreate, db: AsyncSession = Depends(get_db), payload: dict = Depends(require_role("COMPANY"))
):
    application = await ApplicationRepository.get(db, body.application_id)
    if not application or application.job.company_id != payload["linked_id"]:
        raise HTTPException(status_code=403, detail="Not your job listing")
    await PlacementService.issue_offer(db, body.application_id, body.package_lpa)
    application = await ApplicationRepository.get(db, body.application_id)
    return serialize_application(application)


@router.patch("/{application_id}/respond", response_model=ApplicationOut)
async def respond_to_offer(
    application_id: int,
    body: OfferRespondRequest,
    db: AsyncSession = Depends(get_db),
    payload: dict = Depends(require_role("STUDENT")),
):
    await PlacementService.respond_to_offer(db, application_id, payload["linked_id"], body.accept)
    application = await ApplicationRepository.get(db, application_id)
    return serialize_application(application)
