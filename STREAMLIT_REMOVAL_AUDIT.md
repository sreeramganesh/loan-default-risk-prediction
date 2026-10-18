# Streamlit Removal & Project File Audit Report

**Project:** LoanGuard AI — AI-Powered Loan Default Risk Prediction and Verification  
**Repository:** [github.com/sreeramganesh/loan-default-risk-prediction](https://github.com/sreeramganesh/loan-default-risk-prediction)  
**Live Production URL (Render):** [https://loan-default-risk-prediction-ro68.onrender.com](https://loan-default-risk-prediction-ro68.onrender.com)  
**Author:** S Sreeram Ganesh  
**Role:** Senior Python Flask Developer, DevOps Engineer, and Technical Documentation Specialist  
**Document Name:** `STREAMLIT_REMOVAL_AUDIT.md`  
**Date:** October 18, 2026  
**Status:** Audit Complete — Pre-Removal Verification  

---

## 1. Executive Summary & Audit Context

The Flask web application for **LoanGuard AI** is now live and fully operational on **Render** at:  
👉 **`https://loan-default-risk-prediction-ro68.onrender.com`**

The repository owner has designated **Flask** as the **sole, officially supported web application** and **Render** as the **sole production hosting target** for this project.

This audit systematically evaluates every file and directory in the repository to determine what must be retained, modified, or safely removed. The goal is to eliminate obsolete Streamlit deployment references, Streamlit-specific configuration, and unused packages without risking any shared assets, trained models, Flask endpoints, or training pipelines.

---

## 2. File & Component Classification Inventory

Each file in the repository has been audited across eight explicit operational categories:
1. **Flask Core:** Required by the Flask application and web server.
2. **ML Inference:** Required for model prediction, encoding, and risk scoring.
3. **Render Deployment:** Required for cloud container builds and execution on Render.
4. **Streamlit-Exclusive:** Used solely by the obsolete Streamlit application.
5. **Shared Resource:** Shared between multiple tools or components.
6. **Documentation & Governance:** Legal, repository guides, and documentation.
7. **Offline Training:** Required for model training and dataset ingestion; not loaded at runtime.
8. **Development Tooling:** Local editor and environment settings.

| Path | Category | Purpose | Action | Detailed Rationale |
|---|---|---|---|---|
| `app.py` | Flask Core / Render Deployment | Main Flask WSGI application, routes (`/`, `/predict`, `/charts/<filename>`, `/api/metrics`, `/health`), input sanitization, and inference handler. | **RETAIN** | Core production web application. |
| `Procfile` | Render Deployment | Declares cloud WSGI startup command: `web: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app`. | **RETAIN** | Required by Render to launch the web service with appropriate memory isolation. |
| `.python-version` | Render Deployment | Specifies runtime Python version (`3.11`). | **RETAIN** | Ensures Render and buildpacks compile matching binary wheels for scikit-learn. |
| `requirements.txt` | Render Deployment / Dependencies | Python package dependencies for build and runtime. | **MODIFY** | Remove Streamlit-exclusive dependencies (`streamlit>=1.30.0` and `pillow>=10.0.0`). Preserve Flask, Gunicorn, Scikit-learn, Pandas, NumPy, Joblib, Matplotlib, OpenPyXL, and Flask-CORS. |
| `templates/index.html` | Flask Core | Semantic HTML5 dashboard template, dark glassmorphic layout, dual-slider cards, chart gallery, modals. | **RETAIN** | Exact user interface to be preserved 100% without modification. |
| `static/css/style.css` | Flask Core | Bespoke CSS design tokens, HSL color schemes, responsive grid, animations. | **RETAIN** | Frontend styling. Preserved 100% without modification. |
| `static/js/main.js` | Flask Core | Client-side reactive math (instant DTI/PTI recalculation), slider synchronization, AJAX fetch to `/predict`. | **RETAIN** | Frontend interactive script. Preserved 100% without modification. |
| `Models/loan_prediction.pkl` | ML Inference | Pre-trained Random Forest Classifier (34.6 MB). | **RETAIN** | Core predictive asset for underwriting default risk. |
| `Models/feature_encoders.pkl` | ML Inference | Pre-fitted categorical `LabelEncoder` mappings for `application_type`, `verification_status`, and `home_ownership`. | **RETAIN** | Necessary for categorical data preprocessing in `app.py`. |
| `Models/target_encoder.pkl` | ML Inference | Pre-fitted target `LabelEncoder` for decoding numeric predictions back to business labels (`Fully Paid`, `Charged Off`, `Current`). | **RETAIN** | Necessary for output labeling in `app.py`. |
| `src/images/` (8 PNG files) | Flask Core / Shared | Diagnostic model evaluation charts (`Model_Performance_Comparison.png`, `Model_Comparison_Confusion_Matrices.png`, `Class_Performance_Comparison.png`, `Feature_Importance_Comparison.png`, `Target_Class_Distribution.png`, etc.). | **RETAIN** | Served directly by Flask via `GET /charts/<path:filename>` in the Model Comparison tab. |
| `src/Loan_Prediction.py` | Offline Training | End-to-end data processing, feature engineering, model training, evaluation, and chart generation script. | **RETAIN** | Core data science pipeline. Retained for model reproducibility and retraining. |
| `src/Decision tree.py` | Offline Training | Baseline Decision Tree training and evaluation script. | **RETAIN** | Research benchmark code. |
| `src/Random_Forest.py` | Offline Training | Baseline Random Forest training and evaluation script. | **RETAIN** | Research benchmark code. |
| `Data/Loan_Data.csv` | Offline Training | Raw CSV dataset (5.88 MB / 38,574 historical loan records). | **RETAIN** | Historical training data for offline pipeline. Not loaded into memory by `app.py`. |
| `Data/Loan_Data.xlsx` | Offline Training | Normalized relational Excel workbook with 7 dimension and fact sheets (10.51 MB). | **RETAIN** | Historical relational source data for offline pipeline. |
| `LICENSE` | Documentation & Governance | MIT License designating S Sreeram Ganesh as copyright owner. | **RETAIN** | Legal repository governance. Unchanged. |
| `.gitignore` | Development Tooling | Specifies files excluded from Git tracking (`.venv/`, `__pycache__/`, `.idea/`, etc.). | **RETAIN** | Essential git configuration. |
| `test.py` | Development Tooling | Simple local smoke test script verifying Pandas import. | **RETAIN** | Scratch utility. |
| `streamlit_app.py` | Streamlit-Exclusive | Legacy monolithic Streamlit UI, widgets, and layout (1,284 lines / 52.3 KB). | **REMOVE** | Obsolete application entry point. Superseded entirely by Flask (`app.py`). |
| `.streamlit/config.toml` | Streamlit-Exclusive | Theme colors and server parameters specific to Streamlit Cloud. | **REMOVE** | Obsolete configuration directory and file. |
| `README.md` | Documentation & Governance | Project landing page. Currently documents Streamlit Cloud badges, setup, and obsolete workflows. | **MODIFY** | Rewrite completely to document Flask, Render deployment, architecture, ML logic, and live production endpoints. |

---

## 3. Dependency Impact Assessment (`requirements.txt`)

A comprehensive audit of import statements across all retained Python files (`app.py`, `src/Loan_Prediction.py`, `src/Decision tree.py`, `src/Random_Forest.py`, and `test.py`) was performed:

| Package | Status in Requirements | Imported By Retained Code? | Removal Impact & Decision |
|---|---|---|---|
| `streamlit` | Current: `>=1.30.0` | **NO.** Only imported in `streamlit_app.py`. | **SAFE TO REMOVE.** Eliminates ~150 MB of unnecessary build artifacts (Altair, PyDeck, Tornado) on Render. |
| `pillow` | Current: `>=10.0.0` | **NO.** Only imported as `from PIL import Image` in `streamlit_app.py`. Flask serves charts via `send_from_directory()`. | **SAFE TO REMOVE.** Eliminates unneeded C-extension image processing library. |
| `Flask` | Current: `>=3.0.0` | **YES.** `app.py` | **MUST RETAIN.** Core WSGI web application framework. |
| `flask-cors` | Current: `>=4.0.0` | **YES.** `app.py` | **MUST RETAIN.** Cross-Origin Resource Sharing middleware. |
| `gunicorn` | Current: `>=21.2.0` | **YES.** `Procfile` / Render | **MUST RETAIN.** Production WSGI server for Render Linux environment. |
| `scikit-learn` | Current: `>=1.4.0` | **YES.** `app.py`, `src/Loan_Prediction.py` | **MUST RETAIN.** Unpickles and executes Random Forest model and encoders. |
| `pandas` | Current: `>=2.0.0` | **YES.** `app.py`, `src/Loan_Prediction.py` | **MUST RETAIN.** Constructs feature DataFrame and handles training datasets. |
| `numpy` | Current: `>=1.24.0` | **YES.** `app.py`, `src/Loan_Prediction.py` | **MUST RETAIN.** Vector operations and probability arrays. |
| `joblib` | Current: `>=1.3.0` | **YES.** `app.py`, `src/Loan_Prediction.py` | **MUST RETAIN.** Serializes and deserializes `.pkl` model artifacts. |
| `matplotlib` | Current: `>=3.7.0` | **YES.** `src/Loan_Prediction.py` | **MUST RETAIN.** Offline chart generation for `src/images/`. |
| `seaborn` | Current: `>=0.12.0` | Optional for data visualization in training. | **RETAIN.** Preserved for offline EDA and training visualization. |
| `openpyxl` | Current: `>=3.1.0` | **YES.** `src/Loan_Prediction.py` | **MUST RETAIN.** Engine for `pd.read_excel('Data/Loan_Data.xlsx')`. |

---

## 4. Documentation Supersession Audit

The following deployment reports exist or have been prepared:
1. `FLASK_DEPLOYMENT_AUDIT.md`: Historical initial audit evaluating the feasibility of migrating from Streamlit to Flask on Render. (Label as Historical / Superseded).
2. `FLASK_DEPLOYMENT_PREPARATION_REPORT.md`: Step-by-step local preparation report. (Label as Historical / Superseded).
3. `FLASK_DEPLOYMENT_FINAL_REPORT.md`: Pre-deployment verification report. (Label as Historical / Superseded by live deployment).
4. `RENDER_DEPLOYMENT_GUIDE.md`: **NEW canonical documentation** containing the complete, verified, post-deployment guide for developers and contributors.

---

## 5. Audit Recommendations & Execution Plan

1. **Delete Streamlit-Exclusive Files:**
   - Delete `streamlit_app.py`
   - Delete `.streamlit/config.toml` and remove the `.streamlit/` directory.
2. **Update `requirements.txt`:**
   - Remove `streamlit>=1.30.0`
   - Remove `pillow>=10.0.0`
   - Keep all other dependencies cleanly organized.
3. **Rewrite `README.md`:**
   - Establish Flask as the sole application and Render as the official host.
   - Embed live demo URL: `https://loan-default-risk-prediction-ro68.onrender.com`.
   - Embed repository URL: `https://github.com/sreeramganesh/loan-default-risk-prediction`.
   - Include complete local setup, system architecture, and deployment instructions.
4. **Create Canonical Deployment Guide:**
   - Generate `RENDER_DEPLOYMENT_GUIDE.md`.
5. **Create GitHub Profile README Suggestion:**
   - Generate `GITHUB_PROFILE_README_SUGGESTION.md` featuring LoanGuard AI.
6. **Post-Cleanup Regression Testing:**
   - Run end-to-end import, route, prediction, and image serving tests on the Flask application to verify 100% operational integrity.
