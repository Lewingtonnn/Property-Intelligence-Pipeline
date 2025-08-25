# scraper.py

import asyncio
import random
import logging
from playwright.async_api import async_playwright, Page, Error as PlaywrightError
from tenacity import retry, wait_fixed, stop_after_attempt, retry_if_exception_type
from typing import List, Dict
from config import SCRAPER_CONFIG, USER_AGENTS
from data_extractor import DataExtractor
from metrics.metrics import VALIDATION_FAILURES, VALIDATION_SUCCESS
import aiobotocore.session

logger = logging.getLogger(__name__)


# Reusable retry logic for page navigation
@retry(
    wait=wait_fixed(2),
    stop=stop_after_attempt(3),
    retry=(retry_if_exception_type(PlaywrightError) | retry_if_exception_type(asyncio.TimeoutError)),
    reraise=True
)
async def goto_with_retry(page: Page, url: str, timeout: int = 60000):
    """Attempts to navigate to a URL with robust retry logic."""
    logger.info(f"Attempting navigation to: {url}")
    await page.goto(url, timeout=timeout, wait_until="load")
    logger.info(f"Successfully navigated to: {url}")


class ApartmentScraper:
    def __init__(self, playwright_instance):
        self.playwright = playwright_instance
        self.browser = None
        self.context = None

    async def __aenter__(self):
        """Context manager to manage browser lifecycle."""
        self.browser = await self.playwright.firefox.launch(
            headless=SCRAPER_CONFIG['HEADLESS_MODE'],
            args=["--disable-http2", "--disable-features=AutomationControlled", "--disable-web-security"]
        )
        self.context = await self.browser.new_context(user_agent=random.choice(USER_AGENTS))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ensures the browser and context are closed."""
        if self.browser:
            await self.browser.close()

    async def scrape_all_pages(self, main_url: str) -> List[str]:
        """Navigates pagination and collects all property URLs."""
        # ... (This method remains unchanged) ...
        property_urls_set = set()
        current_page_number = 1
        page = await self.context.new_page()
        try:
            await goto_with_retry(page, main_url)
            while True:
                logger.info(f"Scraping page {current_page_number}...")
                try:
                    await page.wait_for_selector('a.property-link', timeout=SCRAPER_CONFIG['TIMEOUTS']['MAIN_PAGE'])
                except PlaywrightError:
                    logger.warning(f"No property links found on page {current_page_number}, ending pagination.")
                    break
                await page.wait_for_timeout(SCRAPER_CONFIG['DELAYS']['AFTER_PAGE_LOAD'])
                property_links = page.locator('a.property-link')
                count = await property_links.count()
                for i in range(count):
                    href = await property_links.nth(i).get_attribute('href')
                    if href:
                        if not href.startswith('http'):
                            href = page.url.rstrip('/') + '/' + href.lstrip('/')
                        property_urls_set.add(href)
                next_page_button = page.locator('a.next')
                if not await next_page_button.is_visible() or await next_page_button.is_disabled():
                    logger.info("No more pages found. Ending pagination.")
                    break
                logger.info("Clicking the 'next' page button...")
                await next_page_button.click()
                await page.wait_for_selector('a.property-link', timeout=SCRAPER_CONFIG['TIMEOUTS']['NEXT_PAGE'])
                current_page_number += 1
                await page.wait_for_timeout(SCRAPER_CONFIG['DELAYS']['BETWEEN_CLICKS'])

        except Exception as e:
            logger.error(f"Error during multi-page scraping: {e}", exc_info=True)
        finally:
            if not page.is_closed():
                await page.close()

        if not page.is_closed():
            await page.close()
        logger.info(f"Scraping complete. Extracted {len(property_urls_set)} unique property URLs.")
        return list(property_urls_set)


    async def scrape_single_property_page(self, url: str) -> Dict:
        """
        New method to scrape a single property page.
        This is the core, reusable consumer logic.
        """
        page = await self.context.new_page()
        try:
            logger.info(f"Starting detail scrape for URL: {url}")
            await goto_with_retry(page, url)

            extractor = DataExtractor(page)
            scraped_data = await extractor.extract_data()

            if scraped_data.get('address') == 'N/A':
                scraped_data['validation_status'] = 'Failed: Critical Data Missing'
                VALIDATION_FAILURES.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()
            else:
                scraped_data['validation_status'] = 'Success'
                VALIDATION_SUCCESS.labels(source=SCRAPER_CONFIG['MAIN_URL']).inc()

            logger.info(f"Finished detail scrape for URL: {url} with status: {scraped_data['validation_status']}")

            return scraped_data

        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}", exc_info=True)
            return {'property_link': url, 'validation_status': 'Failed: Exception'}
        finally:
            if not page.is_closed():
                await page.close()
            # This sleep is now managed by the consumer polling loop