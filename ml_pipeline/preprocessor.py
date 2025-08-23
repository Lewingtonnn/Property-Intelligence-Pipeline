# ml_pipeline/preprocessor.py
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline


def get_preprocessor() -> ColumnTransformer:
    """Returns a preprocessor for the ML pipeline."""
    numerical_features = ['bedrooms', 'bathrooms', 'year_built', 'sqft', 'property_reviews']
    categorical_features = ['state', 'listing_verification']

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numerical_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ])
    return preprocessor