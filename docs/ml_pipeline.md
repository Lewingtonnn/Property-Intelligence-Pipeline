# 🧠 Machine Learning Pipeline

The pipeline includes a **rent prediction model** built with scikit-learn.  

---

## ⚙️ ml_configs.py
- Centralized ML configuration (model paths, hyperparameters).

---

## 📥 data_loader.py
- Fetches structured property + floor plan data from PostgreSQL.
- Cleans and prepares features:
  - Bedrooms, bathrooms, sqft, reviews, year built, etc.

---

## ✨ preprocessor.py
- Defines transformation pipeline:
  - StandardScaler for numeric features
  - OneHotEncoder for categorical features
- Built using `ColumnTransformer`.

---

## 🏋️ trainer.py
- Splits data into train/test.
- Trains **Linear Regression model**.
- Evaluates using **MSE** and **R²**.
- Saves pipeline (`preprocessor + model`) into `.pkl`.

---

## 🎶 main.py
- Orchestrates ML pipeline:
  - Load → preprocess → train → evaluate → save model
- Provides error handling.
- Designed for scheduled retraining.

---

## 🔮 Prediction Flow
- Model is loaded at FastAPI startup.
- API endpoint `/predict/rent` uses the trained pipeline.
- Returns rent price predictions in real-time.
