# models/read_models.py
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from sqlmodel import SQLModel

class PropertyRead(BaseModel):
    id: int
    title: str
    city: str
    year_built: Optional[int]
    timestamp: datetime

    class Config:
        from_attributes = True

class FloorPlanRead(BaseModel):
    id: int
    property_id: int
    bedrooms: int
    base_rent: float

    class Config:
        from_attributes = True