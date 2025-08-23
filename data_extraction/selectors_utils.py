# selectors_utils.py
# Centralized CSS selectors for the apartments.com scraper

APARTMENT_SELECTORS = {
    'title': 'h1.propertyName',
    'address_container': '.propertyAddressContainer',
    'street_address': '.delivery-address span',
    'city_state_zip_container': '.propertyAddressContainer h2',
    'city_span': "h2 > span:nth-of-type(2)",
    'state_zip_container': '.stateZipContainer',
    'property_reviews': '.reviewRating',
    'listing_verification': 'span.verifedText',
    'lease_options_container': '.feesPoliciesCard:has-text("Lease Options")',
    'year_built_container': '.feesPoliciesCard:has-text("Property Information") .component-list .column:has-text("Built in")',
    'unit_cards': 'li.unitContainer',
    'apartment_name': '.modelName',
    'rent_price_range': '.rentLabel',
    'bedrooms_attr': 'data-beds',
    'bathrooms_attr': 'data-baths',
    'sqft_col': '.sqftColumn span:not(.screenReaderOnly)',
    'details_sqft_text': '.detailsTextWrapper span',
    'unit': '.unitColumn span[title]',
    'base_rent': '.pricingColumn > span:not(.screenReaderOnly)',
    'availability': '.availableColumn .dateAvailable:not(.screenReaderOnly)',
    'details_link_attr': 'data-unitkey'
}