# routers/analytics_router.py
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from datetime import datetime, timedelta
from fastAPI_app.auth import (Authorisation)
from fastAPI_app.db.database import get_session
from fastAPI_app.dbmodels import Property, Pricing_and_floor_plans
from fastAPI_app.models.read_models import PropertyRead, FloorPlanRead

router = APIRouter()


@router.get("/top/{x}/most-affordable", response_model=List[FloorPlanRead], tags=["Analytics"])
async def get_top_x_most_affordable_properties(
        x: int,
        session: AsyncSession = Depends(get_session),
        is_authorized: str = Depends(Authorisation())
):
    result = await session.exec(
        select(Pricing_and_floor_plans).order_by(Pricing_and_floor_plans.base_rent.asc()).limit(x)
    )
    return result.all()


@router.get("/top/{x}/most-expensive", response_model=List[FloorPlanRead], tags=["Analytics"])
async def get_top_x_most_expensive_properties(
        x: int,
        session: AsyncSession = Depends(get_session),
        is_authorized: str = Depends(Authorisation())
):
    result = await session.exec(
        select(Pricing_and_floor_plans).order_by(Pricing_and_floor_plans.base_rent.desc()).limit(x)
    )
    return result.all()


@router.get("/this-weeks-listings", response_model=List[PropertyRead], tags=["Properties"])
async def get_this_weeks_listings(
        session: AsyncSession = Depends(get_session),
        is_authorized: str = Depends(Authorisation())
):
    one_week_ago = datetime.now() - timedelta(days=7)
    result = await session.exec(select(Property).where(Property.timestamp >= one_week_ago))
    return result.all()


@router.get("/search", response_model=List[PropertyRead], tags=["Properties"])
async def search_properties(
        session: AsyncSession = Depends(get_session),
        is_authorized: str = Depends(Authorisation()),
        city: Optional[str] = None,
        min_bedrooms: Optional[int] = None,
        max_base_rent: Optional[float] = None,
        year_built: Optional[int] = None,
):
    statement = select(Property).join(Pricing_and_floor_plans, isouter=True)

    if city:
        statement = statement.where(Property.city.ilike(f"%{city}%"))
    if min_bedrooms is not None:
        statement = statement.where(Pricing_and_floor_plans.bedrooms >= min_bedrooms)
    if max_base_rent is not None:
        statement = statement.where(Pricing_and_floor_plans.base_rent <= max_base_rent)
    if year_built is not None:
        statement = statement.where(Property.year_built == year_built)

    statement = statement.group_by(Property.id)
    result = await session.exec(statement)
    return result.all()