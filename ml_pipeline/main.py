# ml_pipeline/main.py
import logging
from data_loader import get_raw_data
from trainer import train_and_save_model

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """Main function to run the ML pipeline."""
    try:
        logger.info("Starting ML pipeline execution.")

        logger.info("Step 1: Fetching raw data from database.")
        df = get_raw_data()

        logger.info(f"Successfully fetched {len(df)} records.")

        logger.info("Step 2: Training and saving the model.")
        train_and_save_model(df)

        logger.info("ML pipeline executed successfully.")

    except Exception as e:
        logger.critical(f"An error occurred during ML pipeline execution: {e}", exc_info=True)


if __name__ == '__main__':
    main()