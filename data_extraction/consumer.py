# consumer.py

import asyncio
import logging
import os
import aiobotocore.session
from dotenv import load_dotenv
from playwright.async_api import async_playwright
import time
from data_extraction.scraper import ApartmentScraper
from config import SCRAPER_CONFIG, PROMETHEUS_PORT
from prometheus_client import start_http_server
from metrics.metrics import (
    SCRAPER_SUCCESS, SCRAPER_FAILURES, LISTINGS_SCRAPED,
    SCRAPE_DURATION, MEMORY_USAGE, CPU_USAGE
)
import psutil
from database_ops.db_ops import save_scraped_data_to_db
from logging_config import setup_logging
# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SQS_QUEUE_NAME = 'real-estate-scrape-jobs'
SQS_QUEUE_URL = None


async def get_queue_url_async(session):
    """Asynchronously gets the SQS queue URL."""
    global SQS_QUEUE_URL
    if SQS_QUEUE_URL:
        return SQS_QUEUE_URL
    async with session.create_client('sqs', region_name=os.getenv('AWS_REGION')) as sqs_client:
        response = await sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
        SQS_QUEUE_URL = response['QueueUrl']
        return SQS_QUEUE_URL


async def process_message(sqs_client, message):
    """
    Asynchronously processes a single SQS message by scraping the URL.
    """
    url = message['Body']
    receipt_handle = message['ReceiptHandle']
    start_time = time.time()

    scraped_data = None
    async with async_playwright() as p:
        try:
            async with ApartmentScraper(p) as scraper:
                # Call the new method to scrape a single URL
                scraped_data = await scraper.scrape_single_property_page(url)

                if scraped_data.get('validation_status') == 'Success':
                    SCRAPER_SUCCESS.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()
                    LISTINGS_SCRAPED.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()
                    logger.info(f"Successfully scraped and validated data for {url}.")

                    # Save data to database
                    await save_scraped_data_to_db([scraped_data])

                    # Delete message on success
                    await sqs_client.delete_message(
                        QueueUrl=SQS_QUEUE_URL,
                        ReceiptHandle=receipt_handle
                    )
                    logger.info(f"Successfully deleted message for {url} from queue.")

                else:
                    SCRAPER_FAILURES.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()
                    # Do not delete message. SQS will handle retries and DLQ.
                    logger.error(f"Validation failed for URL: {url}. Error: {scraped_data.get('validation_status')}")

        except Exception as e:
            SCRAPER_FAILURES.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()
            logger.critical(f"Critical error processing URL {url}: {e}", exc_info=True)
        finally:
            end_time = time.time()
            duration = end_time - start_time
            SCRAPE_DURATION.labels(source=SCRAPER_CONFIG['MAIN_URL']).observe(duration)
            MEMORY_USAGE.set(psutil.virtual_memory().used / 1024 / 1024)
            CPU_USAGE.set(psutil.cpu_percent())


async def poll_sqs_for_messages():
    """
    Continuously polls SQS for new messages asynchronously.
    """
    session = aiobotocore.session.get_session()
    try:
        await get_queue_url_async(session)
    except Exception as e:
        logger.critical(f"Failed to get SQS Queue URL: {e}", exc_info=True)
        return

    async with session.create_client('sqs', region_name=os.getenv('AWS_REGION')) as sqs_client:
        logger.info("Starting SQS consumer...")
        while True:
            try:
                # WaitTimeSeconds is crucial for long-polling
                response = await sqs_client.receive_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MaxNumberOfMessages=1,
                    WaitTimeSeconds=20
                )

                if 'Messages' in response:
                    for message in response['Messages']:
                        # The core logic is now in a separate function
                        await process_message(sqs_client, message)
                else:
                    logger.info("No messages in queue. Waiting...")

            except Exception as e:
                logger.error(f"An error occurred during polling: {e}", exc_info=True)
                await asyncio.sleep(10)  # Wait before retrying to prevent a tight loop


if __name__ == "__main__":
    start_http_server(PROMETHEUS_PORT)
    logger.info("Prometheus HTTP server started.")
    asyncio.run(poll_sqs_for_messages())
    logger.info("Consumer process exited.")