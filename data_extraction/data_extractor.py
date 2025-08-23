# data_extractor.py
import logging
from playwright.async_api import Page
from typing import Dict, List
from selectors_utils import APARTMENT_SELECTORS

logger = logging.getLogger(__name__)


# We'll move your safe helpers here
async def safe_inner_text(locator) -> str:
    """Safely gets inner text from a locator, returns 'N/A' on failure."""
    try:
        text = await locator.inner_text()
        return text.strip() if text else "N/A"
    except Exception as e:
        logger.debug(f"Could not get inner_text: {e}")
    return "N/A"


async def safe_get_attribute(locator, attribute: str) -> str:
    """Safely gets an attribute value from a locator, returns 'N/A' on failure."""
    try:
        attr_value = await locator.get_attribute(attribute)
        return attr_value.strip() if attr_value else "N/A"
    except Exception as e:
        logger.debug(f"Could not get attribute '{attribute}': {e}")
    return "N/A"


class DataExtractor:
    def __init__(self, page: Page):
        self.page = page

    async def extract_data(self) -> Dict:
        """Extracts all apartment details from a single page."""
        data = {
            'property_link': self.page.url,
            'title': 'N/A', 'address': 'N/A', 'street': 'N/A',
            'city': 'N/A', 'state': 'N/A', 'zip_code': 'N/A',
            'property_reviews': '0', 'listing_verification': 'N/A',
            'lease_options': 'N/A', 'year_built': 'N/A',
            'property_type': "Apartment",
            'pricing_and_floor_plans': []
        }

        # Check if it's a standard page before proceeding
        if not await self.page.locator(APARTMENT_SELECTORS['title']).count():
            logger.warning("Standard title not found. Skipping detailed extraction.")
            return data

        # Extract main details using our safe helpers
        data['title'] = await safe_inner_text(self.page.locator(APARTMENT_SELECTORS['title']))
        data['street'] = await safe_inner_text(self.page.locator(APARTMENT_SELECTORS['street_address']))

        # Robust address parsing logic
        state_zip_locator = self.page.locator(APARTMENT_SELECTORS['state_zip_container'])
        data['state'] = await safe_inner_text(state_zip_locator.locator('span').nth(0))
        data['zip_code'] = await safe_inner_text(state_zip_locator.locator('span').nth(1))
        data['city'] = await safe_inner_text(self.page.locator(APARTMENT_SELECTORS['city_span']))

        data['address'] = ", ".join(
            filter(lambda x: x != 'N/A', [data['street'], data['city'], data['state'], data['zip_code']])).strip()

        data['property_reviews'] = await safe_inner_text(self.page.locator(APARTMENT_SELECTORS['property_reviews']))
        data['listing_verification'] = await safe_inner_text(
            self.page.locator(APARTMENT_SELECTORS['listing_verification']))

        # Extracting Lease Options and Year Built
        data['lease_options'] = await self._extract_list_items(APARTMENT_SELECTORS['lease_options_container'])
        data['year_built'] = await self._extract_year_built(APARTMENT_SELECTORS['year_built_container'])

        # Extracting pricing and floor plans
        data['pricing_and_floor_plans'] = await self._extract_floor_plans()

        return data

    async def _extract_list_items(self, container_selector: str) -> List[str]:
        """Generic helper to extract list items from a given container."""
        items = []
        container = self.page.locator(container_selector)
        if await container.count() > 0:
            elements = container.locator('.component-list .column')
            for i in range(await elements.count()):
                option = await safe_inner_text(elements.nth(i))
                if option != "N/A":
                    items.append(option)
        return items if items else ['N/A']

    async def _extract_year_built(self, selector: str) -> str:
        """Extracts the year built using a specific pattern."""
        year_built_text = await safe_inner_text(self.page.locator(selector))
        if "Built in" in year_built_text:
            try:
                return year_built_text.split('Built in ')[-1].split(' ')[0].strip()
            except IndexError:
                logger.warning(f"Could not parse year built from '{year_built_text}'")
        return 'N/A'

    async def _extract_floor_plans(self) -> List[Dict]:
        """Extracts floor plan details from all unit cards."""
        all_units_data = []
        unit_cards_locators = self.page.locator(APARTMENT_SELECTORS['unit_cards'])
        unit_cards_count = await unit_cards_locators.count()
        limit = min(unit_cards_count, 30)

        for i in range(limit):
            unit_card = unit_cards_locators.nth(i)
            unit_data = {
                'apartment_name': await safe_inner_text(unit_card.locator(APARTMENT_SELECTORS['apartment_name'])),
                'rent_price_range': await safe_inner_text(unit_card.locator(APARTMENT_SELECTORS['rent_price_range'])),
                'bedrooms': await safe_get_attribute(unit_card, APARTMENT_SELECTORS['bedrooms_attr']),
                'bathrooms': await safe_get_attribute(unit_card, APARTMENT_SELECTORS['bathrooms_attr']),
                'sqft': await self._extract_sqft(unit_card),
                'unit': await safe_inner_text(unit_card.locator(APARTMENT_SELECTORS['unit'])),
                'base_rent': await safe_inner_text(unit_card.locator(APARTMENT_SELECTORS['base_rent'])),
                'availability': await self._extract_availability(unit_card),
                'details_link': await safe_get_attribute(unit_card, APARTMENT_SELECTORS['details_link_attr'])
            }
            all_units_data.append(unit_data)
        return all_units_data

    async def _extract_sqft(self, unit_card) -> str:
        """Robust SQFT extraction logic."""
        sqft_val = await safe_inner_text(unit_card.locator(APARTMENT_SELECTORS['sqft_col']))
        if sqft_val == "N/A":
            details_spans = unit_card.locator(APARTMENT_SELECTORS['details_sqft_text'])
            for j in range(await details_spans.count()):
                text = await safe_inner_text(details_spans.nth(j))
                if "Sq Ft" in text:
                    return text.replace("Sq Ft", "").strip()
        return sqft_val

    async def _extract_availability(self, unit_card) -> str:
        """Extracts and cleans availability data."""
        availability_raw = await safe_inner_text(unit_card.locator(APARTMENT_SELECTORS['availability']))
        cleaned = availability_raw.split('\n')[-1]
        return cleaned.strip() if cleaned else 'N/A'