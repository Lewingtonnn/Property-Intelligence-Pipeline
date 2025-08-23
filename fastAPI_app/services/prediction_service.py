# services/prediction_service.py
import logging
import pandas as pd
from typing import Optional
from fastAPI_app.db.database import model

logger = logging.getLogger(__name__)


async def predict_rent_service(
        bedrooms: int,
        bathrooms: float,
        property_reviews: float,
        sqft: int,
        year_built: Optional[int],
        state: Optional[str],
        listing_verification: Optional[str]
) -> float:
    """Transforms input data and calls the ML model for prediction."""
    if model.model is None:
        raise RuntimeError("Prediction model is not loaded.")

    input_data = pd.DataFrame({
        'bedrooms': [bedrooms],
        'bathrooms': [bathrooms],
        'year_built': [year_built],
        'property_reviews': [property_reviews],
        'sqft': [sqft],
        'state': [state] if state else ['Unknown'],
        'listing_verification': [listing_verification] if listing_verification else ['Unknown']
    })

    prediction = model.predict(input_data)
    return prediction[0]