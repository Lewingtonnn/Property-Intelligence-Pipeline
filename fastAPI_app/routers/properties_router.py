# routers/properties_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastAPI_app.auth import Authorisation
from fastAPI_app.db.database import get_session
from fastAPI_app.dbmodels import Property, Pricing_and_floor_plans
from fastAPI_app.models.read_models import PropertyRead, FloorPlanRead

router = APIRouter()


@router.get("/", response_model=List[PropertyRead], tags=["Properties"])
async def get_all_properties(
        session: AsyncSession = Depends(get_session),
        is_authorized: str = Depends(Authorisation())
):
    result = await session.exec(select(Property))
    return result.all()


@router.get("/{property_id}/floor-plans", response_model=List[FloorPlanRead], tags=["Floor Plans"])
async def get_floor_plans(
        property_id: int,
        session: AsyncSession = Depends(get_session),
        is_authorized: str = Depends(Authorisation())
):
    property_exists = await session.exec(select(Property).where(Property.id == property_id))
    if not property_exists.first():
        raise HTTPException(status_code=404, detail="Property with that ID is not available.")

    result = await session.exec(
        select(Pricing_and_floor_plans).where(Pricing_and_floor_plans.property_id == property_id)
    )
    return result.all()