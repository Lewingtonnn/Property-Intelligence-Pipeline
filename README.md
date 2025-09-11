# 🏡 Property Intelligence Pipeline
**Enterprise-Grade Real Estate Data Extraction, Analytics & Prediction**


[![Docker](https://img.shields.io/badge/docker-ready-blue)](https://www.docker.com/)  
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)  
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🚀 Overview
The **Property Intelligence Pipeline** is a production-grade system that automates the **extraction, storage, analytics, and prediction** of real estate data at scale.  

**This pipeline reduces property data collection from weeks of manual work to live updates in under 60s, enabling real estate investors to identify trends 90% faster**

It is designed for:  
- **Resilience** → Async scraping + fault-tolerant queues  
- **Scalability** → Decoupled Producer-Consumer model  
- **Observability** → Full Prometheus + Grafana monitoring  
- **Intelligence** → ML-powered rent predictions  

📊 **End result:** A system that not only collects real estate listings but also transforms them into actionable insights.  

---

## 🏗️ System Architecture

![System Architecture](https://github.com/Lewingtonnn/Property-Intelligence-Pipeline/blob/master/images/whole_architecture.jpg)

**Core Flow:**  
Producer → SQS Queue → Consumer → PostgreSQL → FastAPI → Grafana/Prometheus → ML Pipeline  

---

## 🔑 Features
✅ Distributed scraping with **Playwright** + async concurrency  
✅ **AWS SQS** queue for fault tolerance & scaling  
✅ **PostgreSQL** persistence with robust upsert logic  
✅ **FastAPI** service exposing data + analytics + ML predictions  
✅ **ML Pipeline** for rent prediction (Linear Regression + preprocessing)  
✅ **Prometheus & Grafana** observability stack  
✅ **Docker Compose** deployment for the full stack  
✅ **CI/CD** with GitHub Actions  

---

## ⚡ Quick Start (5 min)

**Requirements:**  
- Python 3.10+  
- Docker + Docker Compose  
- AWS SQS credentials  

```bash
# Clone the repo
git clone https://github.com/YourUser/Property-Intelligence-Pipeline.git
cd Property-Intelligence-Pipeline

# Start the full stack
docker-compose up --build
````

* FastAPI Docs → [http://localhost:8000/docs](http://localhost:8000/docs)
* Grafana → [http://localhost:3000](http://localhost:3000)

---

## 📡 API Endpoints

![fastAPI screenshots](https://github.com/Lewingtonnn/Property-Intelligence-Pipeline/blob/master/images/Screenshot%20(108).png) 
![SCREENSHOT2](https://github.com/Lewingtonnn/Property-Intelligence-Pipeline/blob/master/images/Screenshot%20(109).png)
![PRECICTION ENDPOINT](https://github.com/Lewingtonnn/Property-Intelligence-Pipeline/blob/master/images/Screenshot%20(116).png)

| Endpoint                             | Description                          |
| ------------------------------------ | ------------------------------------ |
| `/properties/`                       | List all properties                  |
| `/properties/{id}/floor-plans`       | Floor plans for a property           |
| `/analytics/search`                  | Search by filters (city, rent, etc.) |
| `/analytics/top/{x}/most-affordable` | Cheapest floor plans                 |
| `/predict/rent`                      | ML-powered rent prediction           |



📌 Example:

```bash
curl -X GET "http://localhost:8000/predict/rent?bedrooms=2&bathrooms=1&sqft=800&state=CA&year_built=2010" \
  -H "X-Token: your_api_token"
```

---

## 📊 Monitoring & Metrics

The pipeline is fully observable via Prometheus & Grafana.

![Prometheus Dashboard](https://github.com/Lewingtonnn/Property-Intelligence-Pipeline/blob/master/prometheus%20dashboard%20screenshots/Screenshot%20(98).png)

![Grafana Dashboard](https://github.com/Lewingtonnn/Property-Intelligence-Pipeline/blob/master/grafana%20dashboards%20screenshots/Screenshot%20(103).png)

**Key Metrics Tracked:**

* `SCRAPER_SUCCESS` / `SCRAPER_FAILURES`
* `LISTINGS_SCRAPED`
* `DB_INSERT_FAILURES`
* `CPU_USAGE`, `MEMORY_USAGE`
* API request latency & throughput

---

## 🛠️ Tech Stack

* **Python 3.10**, **FastAPI**, **SQLModel**, **Playwright**
* **AWS SQS**, **PostgreSQL**
* **Prometheus**, **Grafana**
* **Docker Compose**
* **GitHub Actions (CI/CD)**

---

## 🗺️ Roadmap

* Kafka-based ingestion for higher scale
* MLflow model registry for production ML serving
* Anomaly detection for fraudulent/duplicate listings
* Multi-region scraping deployment

---

## 📄 License

MIT License – free to use, modify, and distribute.

---

### ✨ Designed for Production. Built for Scale.



