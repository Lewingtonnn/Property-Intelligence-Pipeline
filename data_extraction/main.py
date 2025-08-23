import asyncio
import json
import logging
import time
import psutil
from playwright.async_api import async_playwright
from data_extraction.scraper import ApartmentScraper
from config import SCRAPER_CONFIG, PROMETHEUS_PORT
from metrics.metrics import (
    SCRAPER_SUCCESS, SCRAPER_FAILURES, LISTINGS_SCRAPED,
    SCRAPE_DURATION, MEMORY_USAGE, CPU_USAGE
)
from database_ops.db_ops import save_scraped_data_to_db
from prometheus_client import start_http_server

# Configure logging to be consistent across modules
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(SCRAPER_CONFIG['LOG_FILE_PATH'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


async def run_scraper():
    """
    Orchestrates the entire scraping process.
    """
    logger.info("Starting the data extraction orchestration.")
    start_time = time.time()
    scraped_final_data = []

    try:
        async with async_playwright() as p:
            async with ApartmentScraper(p) as scraper:

                # Step 1: Extract all property URLs
                property_urls = await scraper.scrape_all_pages(SCRAPER_CONFIG['MAIN_URL'])

                # Step 2: Limit properties and scrape details concurrently
                limited_urls = property_urls[:SCRAPER_CONFIG['PROPERTIES_TO_SCRAPE_LIMIT']]
                logger.info(f"Found {len(property_urls)} properties. Scraping details for {len(limited_urls)}.")

                scraped_data = await scraper.scrape_properties_concurrently(limited_urls)

                # Step 3: Process results and count successes/failures
                for res in scraped_data:
                    if isinstance(res, dict) and res.get('validation_status') == 'Success':
                        scraped_final_data.append(res)
                        LISTINGS_SCRAPED.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()
                    else:
                        SCRAPER_FAILURES.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()

                logger.info(f"Total successful property data entries collected: {len(scraped_final_data)}")

    except Exception as e:
        logger.critical(f"A critical error occurred during scraping: {e}", exc_info=True)
        # Handle cleanup and partial data persistence here

    finally:
        stop_time = time.time()
        total_time_taken = stop_time - start_time
        logger.info(f"Scraping completed in {total_time_taken:.2f} seconds.")
        SCRAPE_DURATION.labels(source=SCRAPER_CONFIG['MAIN_URL']).observe(total_time_taken)
        MEMORY_USAGE.set(psutil.virtual_memory().used / 1024 / 1024)
        CPU_USAGE.set(psutil.cpu_percent())

        # Save results to file and database
        if scraped_final_data:
            with open("apartments_data.json", "w", encoding="utf-8") as f:
                json.dump(scraped_final_data, f, ensure_ascii=False, indent=4)
            await save_scraped_data_to_db(scraped_final_data)


if __name__ == '__main__':
    start_http_server(PROMETHEUS_PORT)
    logger.info("Prometheus HTTP server started.")
    asyncio.run(run_scraper())
    logger.info("Exiting.")