# ml_pipeline/trainer.py
import logging
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from preprocessor import get_preprocessor
from sklearn.pipeline import Pipeline
from ml_configs import ML_CONFIG
import os

logger = logging.getLogger(__name__)


def train_and_save_model(df: pd.DataFrame):
    """Trains a linear regression model and saves the pipeline to a file."""
    X = df[['bedrooms', 'bathrooms', 'year_built', 'property_reviews', 'sqft', 'state', 'listing_verification']]
    y = df['base_rent']

    preprocessor = get_preprocessor()

    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', LinearRegression())
    ])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    logger.info("Starting model training...")
    model_pipeline.fit(X_train, y_train)
    logger.info("Model training completed.")

    predictions = model_pipeline.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    logger.info(f"Model evaluation - Mean Squared Error: {mse}")
    logger.info(f"Model evaluation - R-squared: {r2}")

    fastapi_app_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'fastAPI_app'
    )
    model_path = os.path.join(
        fastapi_app_dir,
        'linear_regression_rent_model_pipeline.pkl'
    )

    joblib.dump(model_pipeline, model_path)
    logger.info(f"Model pipeline saved to {model_path}")


