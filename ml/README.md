# ml/ — Machine Learning Module

**Status: Phase 0 — Not yet implemented.**

This module will contain:

| Sub-folder | Contents |
|---|---|
| `data/` | Raw and processed training datasets |
| `features/` | Feature engineering pipelines |
| `models/` | Trained model artefacts (`.joblib`) |
| `notebooks/` | Exploratory analysis notebooks |
| `training/` | Training scripts (XGBoost, scikit-learn) |
| `inference/` | Prediction / SHAP explainability modules |
| `evaluation/` | Metrics, cross-validation, calibration |

**Tech stack:** pandas · numpy · geopandas · rasterio · scikit-learn · XGBoost · imbalanced-learn · SHAP · joblib

> ML logic stays in this module. FastAPI route handlers must never import model objects directly — they call service functions in `backend/app/services/`.
