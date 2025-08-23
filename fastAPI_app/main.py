# main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from prometheus_client import generate_latest
from starlette.responses import Response

from fastAPI_app.APIconfigs import API_CONFIG, PROMETHEUS_METRICS, MODEL_PATH
from fastAPI_app.db.database import create_db_and_tables, get_session, model
from fastAPI_app.routers import properties_router, analytics_router, prediction_router

# Configure logging to be consistent across modules
logging.basicConfig(
    level=logging.INFO,
    format=API_CONFIG['LOG_FORMAT']
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown events for the application."""
    logging.info("Application Startup: Creating database tables if they don't exist.")
    await create_db_and_tables()
    logging.info("Application Startup: Loading pre-trained model.")
    try:
        model.load_model('MODEL_PATH')
        logging.info("Model loaded successfully.")
    except FileNotFoundError:
        logging.critical("Model file not found. Prediction service will be unavailable.")
    except Exception as e:
        logging.critical(f"An error occurred while loading the model: {e}")
    yield
    logging.info("Application Shutdown: Cleaning up process.")


app = FastAPI(
    title=API_CONFIG['TITLE'],
    description=API_CONFIG['DESCRIPTION'],
    version=API_CONFIG['VERSION'],
    lifespan=lifespan
)

# Attach Prometheus middleware
@app.middleware("http")
async def track_requests(request, call_next):
    import time
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    PROMETHEUS_METRICS['REQUEST_COUNT'].labels(endpoint=request.url.path).inc()
    PROMETHEUS_METRICS['REQUEST_LATENCY'].observe(process_time)
    return response

@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    return Response(generate_latest(), media_type="text/plain")

# Include the new routers
app.include_router(properties_router.router, prefix="/properties", tags=["Properties", "Analytics"])
app.include_router(analytics_router.router, prefix="/analytics", tags=["Analytics"])
app.include_router(prediction_router.router, prefix="/predict", tags=["Prediction"])

logging.info("Prometheus metrics endpoint and middleware attached.")

@app.get("/", tags=["Health"])
async def welcome():
    return {"Message": "Welcome to the Real Estate API. See /docs for API documentation."}