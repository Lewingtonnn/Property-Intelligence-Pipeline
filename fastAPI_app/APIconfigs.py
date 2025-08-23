# config.py
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram

load_dotenv()

# Application Settings
API_CONFIG = {
    "TITLE": "Real Estate Data API",
    "DESCRIPTION": "API For Accessing Real Estate Property and Floor Plan Data. Also provides analytics and predictions.",
    "VERSION": "2.0.0",
    "LOG_FORMAT": "%(asctime)s - %(levelname)s - %(message)s"
}

# Database and Security
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set. Please set it to your PostgreSQL database URL.")
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN environment variable is not set.")

# Metrics
PROMETHEUS_METRICS = {
    "REQUEST_COUNT": Counter("api_request_total", "Total API Request", ["endpoint"]),
    "REQUEST_LATENCY": Histogram("api_request_latency_seconds", "Request latency")
}

# Paths
ML_CONFIG = {
    "MODEL_PATH": "linear_regression_rent_model_pipeline.pkl"
}
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "linear_regression_rent_model_pipeline.pkl")
