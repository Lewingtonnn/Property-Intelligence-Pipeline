import asyncio
import logging
import os
import signal
import time

import aiobotocore.session
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from prometheus_client import start_http_server
import psutil

from data_extraction.scraper import ApartmentScraper
from config import SCRAPER_CONFIG, PROMETHEUS_PORT
from metrics.metrics import (
    SCRAPER_SUCCESS, SCRAPER_FAILURES, LISTINGS_SCRAPED,
    SCRAPE_DURATION, MEMORY_USAGE, CPU_USAGE
)
from database_ops.db_ops import save_scraped_data_to_db
from logging_config import setup_logging

# ----------------------------------------------------
# Bootstrap
# ----------------------------------------------------
setup_logging()
logger = logging.getLogger(__name__)
load_dotenv()

SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "real-estate-scrape-jobs")
AWS_REGION = os.getenv("AWS_REGION")
if not AWS_REGION:
    # Fail fast: region is mandatory for SQS
    raise RuntimeError("AWS_REGION is not set in environment")

# Tuning knobs (env overrideable)
BATCH_SIZE = int(os.getenv("CONSUMER_BATCH_SIZE", "10"))  # Max 10 for SQS
CONCURRENCY = int(os.getenv("CONSUMER_CONCURRENCY", "5"))
LONG_POLL_SECONDS = int(os.getenv("SQS_LONG_POLL_SECONDS", "20"))  # up to 20
POLL_IDLE_SLEEP = float(os.getenv("POLL_IDLE_SLEEP", "1.5"))  # seconds when queue empty
ERROR_BACKOFF = float(os.getenv("ERROR_BACKOFF", "10"))  # seconds on unexpected error

SQS_QUEUE_URL = None  # cached after first lookup


# ----------------------------------------------------
# SQS helpers
# ----------------------------------------------------
async def get_queue_url_async(session: aiobotocore.session.AioSession) -> str:
    """Resolve and cache SQS queue URL."""
    global SQS_QUEUE_URL
    if SQS_QUEUE_URL:
        return SQS_QUEUE_URL
    async with session.create_client("sqs", region_name=AWS_REGION) as sqs_client:
        resp = await sqs_client.get_queue_url(QueueName=SQS_QUEUE_NAME)
        SQS_QUEUE_URL = resp["QueueUrl"]
        logger.info(f"Resolved SQS queue URL: {SQS_QUEUE_URL}")
        return SQS_QUEUE_URL


# ----------------------------------------------------
# Core processing
# ----------------------------------------------------
async def process_message(sqs_client, message: dict, scraper: ApartmentScraper):
    """Process a single SQS message: scrape, validate, persist, delete or leave for DLQ."""
    url = message.get("Body")
    receipt_handle = message.get("ReceiptHandle")

    if not url or not receipt_handle:
        logger.error("Malformed SQS message — missing Body or ReceiptHandle; leaving for DLQ.")
        return

    start_time = time.time()

    try:
        scraped_data = await scraper.scrape_single_property_page(url)

        # Defensive check
        if not isinstance(scraped_data, dict):
            raise ValueError("scrape_single_property_page must return a dict with validation_status")

        if scraped_data.get("validation_status") == "Success":
            # Metrics
            SCRAPER_SUCCESS.labels(source=SCRAPER_CONFIG["MAIN_URL"]).inc()
            LISTINGS_SCRAPED.labels(source=SCRAPER_CONFIG["MAIN_URL"]).inc()

            logger.info(f"Scrape OK: {url} — persisting to DB")
            await save_scraped_data_to_db([scraped_data])
            logger.info("Persisted.")

            # Delete message on success
            await sqs_client.delete_message(QueueUrl=SQS_QUEUE_URL, ReceiptHandle=receipt_handle)
            logger.info(f"Deleted message for {url}")
        else:
            # Validation failed — don't delete. Let SQS retry / DLQ
            SCRAPER_FAILURES.labels(source=SCRAPER_CONFIG["MAIN_URL"]).inc()
            logger.warning(
                "Validation failed — not deleting. url=%s reason=%s",
                url, scraped_data.get("validation_status")
            )

    except Exception as e:
        SCRAPER_FAILURES.labels(source=SCRAPER_CONFIG["MAIN_URL"]).inc()
        logger.exception(f"Critical error processing url={url}: {e}")

    finally:
        duration = time.time() - start_time
        SCRAPE_DURATION.labels(source=SCRAPER_CONFIG["MAIN_URL"]).observe(duration)
        MEMORY_USAGE.set(psutil.virtual_memory().used / 1024 / 1024)
        CPU_USAGE.set(psutil.cpu_percent())


async def poll_sqs_for_messages(scraper: ApartmentScraper, stop_event: asyncio.Event):
    """Continuously poll SQS and process messages in batches with limited concurrency."""
    session = aiobotocore.session.get_session()

    try:
        await get_queue_url_async(session)
    except Exception as e:
        logger.exception(f"Failed to get SQS queue URL: {e}")
        return

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with session.create_client("sqs", region_name=AWS_REGION) as sqs_client:
        logger.info(
            f"SQS consumer started — batch_size={BATCH_SIZE} concurrency={CONCURRENCY} long_poll={LONG_POLL_SECONDS}s"
        )

        while not stop_event.is_set():
            try:
                response = await sqs_client.receive_message(
                    QueueUrl=SQS_QUEUE_URL,
                    MaxNumberOfMessages=min(max(BATCH_SIZE, 1), 10),
                    WaitTimeSeconds=min(max(LONG_POLL_SECONDS, 0), 20),
                )

                messages = response.get("Messages", [])
                if not messages:
                    # small idle sleep to avoid busy loop when queue is empty
                    await asyncio.sleep(POLL_IDLE_SLEEP)
                    continue

                # Launch tasks up to concurrency
                tasks = []
                for m in messages:
                    async def _run(msg=m):
                        async with semaphore:
                            await process_message(sqs_client, msg, scraper)
                    tasks.append(asyncio.create_task(_run()))

                # Wait for this batch to settle before next poll (simple model)
                await asyncio.gather(*tasks, return_exceptions=False)

            except asyncio.CancelledError:
                logger.info("Polling cancelled — shutting down cleanly...")
                break
            except Exception as e:
                logger.exception(f"Polling error: {e}. Backing off {ERROR_BACKOFF}s")
                await asyncio.sleep(ERROR_BACKOFF)

        logger.info("Stop signal received — exiting polling loop.")


# ----------------------------------------------------
# Main
# ----------------------------------------------------


async def main():
    # Prometheus endpoint
    start_http_server(PROMETHEUS_PORT)
    logger.info(f"Prometheus HTTP server started on port {PROMETHEUS_PORT}")

    stop_event = asyncio.Event()

    def _handle_signal(signame):
        logger.info(f"Received {signame} — initiating shutdown...")
        stop_event.set()

    # Register signal handlers
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(s, lambda *_: _handle_signal(s.name))
        except Exception:
            pass

    # CORRECT ARCHITECTURE: Launch the browser and scraper once
    # The entire polling loop runs within this context
    async with async_playwright() as p:
        async with ApartmentScraper(p) as scraper:
            await poll_sqs_for_messages(scraper, stop_event)

    logger.info("Consumer process exited.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Unhandled critical error in main: {e}", exc_info=True)