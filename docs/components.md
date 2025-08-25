# 🧩 Core Components

This section breaks down each component of the pipeline.

---

## ⚙️ config.py
- Centralized configuration for all parameters:
  - `PROMETHEUS_PORT`, `SCRAPER_CONFIG`, `USER_AGENTS`, `ML_CONFIG`.
- Prevents magic numbers and centralizes system settings.

---

## 🚀 producer.py
- Discovers property listing URLs.
- Enqueues each URL into **AWS SQS**.
- Key Features:
  - Async Playwright scraping
  - Pagination handling
  - URL filtering/limiting
  - Concurrent enqueueing

---

## 📦 consumer.py
- Polls SQS for messages.
- Scrapes property details.
- Persists data into PostgreSQL.
- Features:
  - Long-lived Playwright browser context
  - Async scraping with concurrency limits
  - Data validation
  - Upsert persistence logic
  - Prometheus metrics
  - Graceful shutdown (SIGINT, SIGTERM)

---

## 🕷️ scraper.py
- Encapsulates Playwright scraping logic.
- Features:
  - Async context manager for browser lifecycle
  - User-agent rotation
  - Resilient retry logic
  - Single property page scraping with validation
  - Defensive scraping (closing pages after use)

---

## 📝 data_extractor.py
- Handles parsing and cleaning of data.
- Fault-tolerant with helper methods (`safe_inner_text`, `safe_get_attribute`).
- Extracts multi-floor plans, normalizes data.

---

## 💾 Database Layer
### dbmodels.py
- SQLModel ORM definitions:
  - `Property` table (listing info, metadata)
  - `Pricing_and_floor_plans` table (unit-level details)

### db_ops.py
- Handles database sessions, inserts, updates.
- Features:
  - Async PostgreSQL engine
  - Upsert logic with rollback on error
  - Numeric parsing & type conversion
  - Timezone-aware timestamps

---

## 📈 FastAPI Layer
- Routers: `/properties`, `/analytics`, `/predict`
- Security: token-based authentication
- Features:
  - Pydantic models for response validation
  - Analytics queries
  - Real-time ML predictions

