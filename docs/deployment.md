# 🚀 Deployment Guide

---

## 🐳 Docker Setup
- Each service is containerized.
- `docker-compose.yml` orchestrates:
  - FastAPI
  - PostgreSQL
  - Prometheus
  - Grafana

---

## 📂 CI/CD (GitHub Actions)
- Workflow: `.github/workflows/deploy.yml`
- On push to `master`:
  - Install dependencies
  - Run tests (pytest)
  - Build Docker image
- Produces reproducible, tested builds.

---

## ☁️ AWS Setup
- **SQS Queue** required.
- Provide credentials via ENV variables:
  - `AWS_ACCESS_KEY_ID`
  - `AWS_SECRET_ACCESS_KEY`
  - `SQS_QUEUE_URL`

---

## 🛠️ Local Development
```bash
docker-compose up --build
```


FastAPI at http://localhost:8000

Grafana at http://localhost:3000


---

