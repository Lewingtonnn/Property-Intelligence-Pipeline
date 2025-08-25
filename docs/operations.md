
# 🧰 Operations & Runbook

---

## ✅ Startup Checklist
1. Ensure AWS SQS is configured.
2. Run `docker-compose up`.
3. Verify:
   - DB tables created
   - ML model loaded
   - Prometheus scraping metrics

---

## ⚠️ Common Issues
- **SQS Connection Failure** → Check credentials and queue URL.
- **Scraper Timeout** → Increase timeout/delay in `SCRAPER_CONFIG`.
- **DB IntegrityError** → Ensure schema matches ORM definitions.
- **Model Not Loading** → Verify correct `MODEL_PATH`.

---

## 🛡️ On-Call Guide
- First check Grafana dashboards.
- Look for spikes in `SCRAPER_FAILURES` or API latency.
- Validate Prometheus targets are healthy.

---

## 🔄 Recovery Procedures
- Restart consumer if scraping fails continuously.
- Replay failed messages from SQS DLQ.
- For DB issues, rollback transaction & re-run.