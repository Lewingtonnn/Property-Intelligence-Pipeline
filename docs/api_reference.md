# 📡 API Reference

The API is powered by **FastAPI** and fully documented via OpenAPI/Swagger.

---

## 🔒 Authentication
- All endpoints require an `X-Token` header.
- Value must match `API_TOKEN` environment variable.

---
![screenshot_1](images/fastapidocs.jpg)
![screenshot_2](images/fastapidocs2.jpg)


## 🏡 Properties
### GET `/properties/`
- Returns list of all properties.

![ENDPOINT](images/getlistings.jpg)

### GET `/properties/{id}/floor-plans`
- Returns floor plans for a given property.
- 404 if not found.

![ENDPOINTS](images/floorplans.png)
---

## 📊 Analytics
### GET `/analytics/top/{x}/most-affordable`
- Returns top `x` cheapest floor plans.

![ENDPOINT](images/topmostexpensive.jpg)

### GET `/analytics/top/{x}/most-expensive`
- Returns top `x` most expensive floor plans.
![ENDPOINT](images/topmostaffordable.jpg)

### GET `/analytics/this-weeks-listings`
- Listings added in last 7 days.

![ENDPOINT](images/thisweekslistings.jpg)

### GET `/analytics/search`
- Search by filters:
  - `city`
  - `min_bedrooms`
  - `max_base_rent`
  - `year_built`

![FAST API ENDPOINTS analytics](images/searchproperty.jpg)

---

## 🔮 Predictions
### GET `/predict/rent`
- Input: bedrooms, bathrooms, sqft, state, year_built
- Output: predicted rent price.

![ENDPOINT](images/prediction.jpg)




Example:
```bash
curl -X GET "http://localhost:8000/predict/rent?bedrooms=2&bathrooms=1&sqft=800&state=CA&year_built=2010" \
  -H "X-Token: your_api_token"

