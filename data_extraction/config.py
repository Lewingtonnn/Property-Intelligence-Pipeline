# Centralized configuration for the scraper

PROMETHEUS_PORT = 8001

SCRAPER_CONFIG = {
    'MAIN_URL': 'https://www.apartments.com/boston-ma/',
    'PROPERTIES_TO_SCRAPE_LIMIT': 10,
    'MAX_CONCURRENT_PAGES': 10,
    'HEADLESS_MODE': True,
    'LOG_FILE_PATH': 'DataExtraction.log',
    'TIMEOUTS': {
        'MAIN_PAGE': 30000,
        'NEXT_PAGE': 30000,
    },
    'DELAYS': {
        'AFTER_PAGE_LOAD': 1000,
        'BETWEEN_CLICKS': 1000,
        'AFTER_SCRAPE_MIN': 1,
        'AFTER_SCRAPE_MAX': 3,
    }
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.86 Mobile Safari/537.36"
]

ML_CONFIG = {
    "MODEL_PATH": "ml_pipeline/linear_regression_rent_model_pipeline.pkl"
}
