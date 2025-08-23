# routers/prediction_router.py
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastAPI_app.auth import Authorisation
from fastAPI_app.services.prediction_service import predict_rent_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/rent", response_model=float, tags=["Prediction"])
async def predict_rent(
    bedrooms: int,
    bathrooms: float,
    property_reviews: float,
    sqft: int,
    year_built: Optional[int] = None,
    state: Optional[str] = None,
    listing_verification: Optional[str] = None,
    is_authorized: str = Depends(Authorisation())
):
    try:
        prediction = await predict_rent_service(
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            property_reviews=property_reviews,
            sqft=sqft,
            year_built=year_built,
            state=state,
            listing_verification=listing_verification
        )
        return float(prediction)
    except RuntimeError as e:
        logger.error(f"Prediction service unavailable: {e}")
        raise HTTPException(status_code=503, detail="Prediction service is temporarily unavailable. The model is not loaded.")
    except Exception as e:
        logger.error(f"Error during rent prediction: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")