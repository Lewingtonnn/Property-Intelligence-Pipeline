# ml_pipeline/data_loader.py
import pandas as pd
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_raw_data() -> pd.DataFrame:
    """Fetches raw property and floor plan data from the database."""
    database_url = os.getenv("SyncDatabase_URL")
    if not database_url:
        raise ValueError("SyncDatabase_URL environment variable is not set.")

    engine = create_engine(database_url)
    df = pd.read_sql("""
        SELECT 
            property.state, 
            T1.bedrooms, 
            T1.bathrooms, 
            property.year_built, 
            property.property_reviews, 
            property.listing_verification, 
            T1.base_rent, 
            T1.sqft 
        FROM 
            pricing_and_floor_plans T1
        JOIN 
            property ON property.id = T1.property_id
    """, engine)

    # Pre-cleaning of data types to avoid pipeline errors
    df['base_rent'] = pd.to_numeric(df['base_rent'], errors='coerce')
    df['sqft'] = pd.to_numeric(df['sqft'], errors='coerce')
    df['year_built'] = pd.to_numeric(df['year_built'], errors='coerce')

    df.dropna(inplace=True)

    return df