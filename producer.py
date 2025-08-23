# producer.py

import asyncio
import logging
import os
from playwright.async_api import async_playwright
import aiobotocore.session
from dotenv import load_dotenv

from data_extraction.scraper import ApartmentScraper  # Note: The scraper class is still needed
from config import SCRAPER_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SQS_QUEUE_NAME = 'real-estate-scrape-jobs'


async def run_producer():
    """
    Orchestrates the process of extracting property URLs and sending them to SQS.
    """
    logger.info("Starting the producer orchestration.")

    session = aiobotocore.session.get_session()
    async with session.create_client('sqs', region_name=os.getenv('AWS_REGION')) as sqs_client:
        try:
            queue_url_res = await sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
            queue_url = queue_url_res['QueueUrl']
            logger.info(f"Successfully connected to SQS queue at {queue_url}.")

        except Exception as e:
            logger.critical(f"Failed to connect to SQS: {e}", exc_info=True)
            return

        async with async_playwright() as p:
            async with ApartmentScraper(p) as scraper:
                # Step 1: Extract all property URLs
                property_urls = await scraper.scrape_all_pages(SCRAPER_CONFIG['MAIN_URL'])

                # Step 2: Limit properties and send URLs to SQS
                limited_urls = property_urls[:SCRAPER_CONFIG['PROPERTIES_TO_SCRAPE_LIMIT']]
                logger.info(f"Found {len(property_urls)} properties. Sending {len(limited_urls)} URLs to SQS.")

                tasks = [sqs_client.send_message(
                    QueueUrl=queue_url,
                    MessageBody=url
                ) for url in limited_urls]

                # Use aio.gather for concurrent message sending
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.info("All messages sent to SQS.")

    logger.info("Producer process completed.")


if __name__ == '__main__':
    asyncio.run(run_producer())