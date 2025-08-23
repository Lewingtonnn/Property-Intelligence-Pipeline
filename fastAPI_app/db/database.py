
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from fastAPI_app.APIconfigs import DATABASE_URL, MODEL_PATH


logger = logging.getLogger(__name__)

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, future=True)

async_session_maker = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def create_db_and_tables():
    """Initializes the database and creates tables from models."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info('Database tables created successfully.')
    except Exception as e:
        logger.critical(f"Failed to create database tables: {e}", exc_info=True)
        raise


async def get_session() -> AsyncSession:
    """Dependency to provide a new database session for each request."""
    async with async_session_maker() as session:
        yield session


# A global, mock model service to be loaded in the app lifespan
class ModelService:
    def __init__(self):
        self.model = None

    def load_model(self, model_path: str):
        import joblib
        self.model = joblib.load(model_path)

    def predict(self, data):
        if self.model is None:
            raise RuntimeError("Model is not loaded.")
        return self.model.predict(data)


model = ModelService()