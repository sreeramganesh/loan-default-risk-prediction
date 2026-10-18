# Render Cloud Deployment Guide for LoanGuard AI

**Project:** Loan Default Risk Prediction / LoanGuard AI  
**Repository:** [github.com/sreeramganesh/loan-default-risk-prediction](https://github.com/sreeramganesh/loan-default-risk-prediction)  
**Author:** S Sreeram Ganesh  
**Primary Framework:** Python / Flask  
**Current Production URL:** [https://loan-default-risk-prediction-ro68.onrender.com](https://loan-default-risk-prediction-ro68.onrender.com)  
**Health Check URL:** [https://loan-default-risk-prediction-ro68.onrender.com/health](https://loan-default-risk-prediction-ro68.onrender.com/health)  
**Document Name:** `RENDER_DEPLOYMENT_GUIDE.md`  
**Date:** October 18, 2026  
**Status:** Live on Render — Operational  

---

## 1. Overview & Current Deployment Status

The **LoanGuard AI** Flask web application is deployed on **Render** as a Free Web Service.

> **Important Deployment Notice:**  
> The current live service at `https://loan-default-risk-prediction-ro68.onrender.com` is operational.  
> Any local code cleanup, documentation updates, or dependency modifications made locally are staged in your local working tree. They will **not take effect on the live website** until they are reviewed, committed, pushed to the GitHub `main` branch, and built by Render.

This document serves as the guide for deploying and maintaining LoanGuard AI on Render.

---

## 2. Prerequisites

Before deploying to Render, verify:
1. **GitHub Account:** Connected to the repository `sreeramganesh/loan-default-risk-prediction`.
2. **Render Account:** Created at [render.com](https://render.com).
3. **Repository Files:** Ensure the following deployment configuration files are present in the repository root:
   - `Procfile`
   - `requirements.txt`
   - `app.py`
   - `.python-version`
   - `Models/` (containing `loan_prediction.pkl`, `feature_encoders.pkl`, `target_encoder.pkl`)
   - `src/images/` (containing diagnostic PNG charts)
   - `templates/index.html`
   - `static/css/style.css`
   - `static/js/main.js`

---

## 3. Step-by-Step Render Deployment Procedure

### Step 1: Prepare & Push the Repository
Check your local Git status and push the latest verified changes:
```bash
# 1. Review status
git status

# 2. Stage updated files
git add Procfile requirements.txt app.py README.md RENDER_DEPLOYMENT_GUIDE.md STREAMLIT_REMOVAL_AUDIT.md

# 3. Commit with a clear message
git commit -m "Remove Streamlit and finalize Flask Render deployment"

# 4. Push to GitHub
git push origin main
```

### Step 2: Sign in to Render Dashboard
1. Open [dashboard.render.com](https://dashboard.render.com/).
2. Log in with your GitHub account.

### Step 3: Create a Web Service
1. Click the blue **New +** button in the upper right.
2. Select **Web Service**.
3. Under **Connect a repository**, find `sreeramganesh/loan-default-risk-prediction` and click **Connect**.  
   *(If your repository is not listed, configure GitHub permissions to grant Render access).*

### Step 4: Configure Web Service Parameters
Enter the exact configuration details:

| Configuration Field | Setting Value | Purpose / Rationale |
|---|---|---|
| **Name** | `loan-default-risk-prediction-ro68` *(or custom)* | Sets your subdomain on `.onrender.com`. |
| **Region** | `Oregon (US West)` or `Frankfurt (EU)` | Choose the region closest to your audience. |
| **Branch** | `main` | Production deployment branch. |
| **Root Directory** | *(leave blank)* | Application is located at repository root. |
| **Runtime** | `Python` | Standard Render Python build environment. |
| **Build Command** | `pip install -r requirements.txt` | Installs Flask, scikit-learn, Gunicorn, and dependencies. |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 app:app` | WSGI startup command matching `Procfile`. |
| **Instance Type** | **Free** ($0/month) | 0.5 vCPU, 512 MB RAM. |

#### Why Single Worker (`--workers 1`)?
- The Random Forest model (`loan_prediction.pkl`) is 33 MB on disk and expands in heap allocation when loaded into memory.
- A single worker process keeps memory usage within the 512 MB Free Tier limit.
- Running multiple workers significantly increases total memory consumption and can trigger Render's Out-Of-Memory (OOM) killer.

#### Why Timeout 120 (`--timeout 120`)?
- Prevents Gunicorn from prematurely killing the worker process during initial model deserialization.

### Step 5: Advanced Configuration
Expand the **Advanced** section at the bottom of the form:

1. **Health Check Path:**
   - Set to: `/health`
   - *Why:* Render monitors this endpoint. A 200 OK response verifies that both Flask and the ML models are initialized before user traffic is routed.
2. **Environment Variables:**
   - Click **Add Environment Variable**:
     - **Key:** `PYTHON_VERSION`
     - **Value:** `3.11.9`
   - *Why:* Locks Python version to match `.python-version` and ensure binary compatibility with scikit-learn wheels.
3. **Auto-Deploy:**
   - Set to: `Yes`
   - *Why:* Any future push to `main` will automatically trigger a rebuild and redeployment on Render.

### Step 6: Trigger Deployment
1. Click **Create Web Service**.
2. Render provisions a Linux container, executes `pip install -r requirements.txt`, starts Gunicorn, verifies `/health`, and marks the service **Live**.

---

## 4. Post-Deployment Verification Checklist

Once Render marks the service status as **Live**, verify each layer:

### 1. Automated Health Check
Run in PowerShell or terminal:
```bash
curl -I https://loan-default-risk-prediction-ro68.onrender.com/health
```
*Expected output:* `HTTP/2 200` with JSON:
```json
{
  "model_loaded": true,
  "service": "LoanGuard AI Flask Service",
  "status": "healthy"
}
```

### 2. Homepage & UI Rendering
1. Open `https://loan-default-risk-prediction-ro68.onrender.com/` in your browser.
2. Confirm the dark glassmorphic styling, ambient background glows, and fonts load properly.
3. Open Developer Tools (F12) &rarr; **Console** tab. Confirm there are no 404 or JavaScript errors.

### 3. Model Inference Test
1. Move the sliders to test a sample applicant (e.g., Loan Amount: $15,000, Income: $85,000, Interest Rate: 11.5%).
2. Verify that the dynamic DTI and payment burden meters recalculate in the browser.
3. Click **Analyze Loan Risk & Verification Status**.
4. Verify that the decision badge, probability gauges, and financial summary populate immediately.

### 4. Model Comparison Chart Inspection
1. Switch to the **Model Comparison & Chart Gallery** tab.
2. Confirm all 5 charts load without broken image icons.
3. Click any chart to open the high-resolution lightbox modal.

---

## 5. Free-Tier Operational Characteristics

| Behavior | Detail | Explanation |
|---|---|---|
| **Sleep after Inactivity** | Spins down after 15 minutes of zero HTTP requests. | Standard Render Free Tier policy. The instance sleeps to conserve shared cloud resources. |
| **Cold Start Behavior** | First request after sleep wakes the container. | Takes an initial delay to boot the container, start Python, and load the ML model into memory. Subsequent requests respond normally once warm. |
| **Memory Limit** | Strict 512 MB RAM ceiling on Free tier. | Keep `--workers 1` enforced to remain within memory allowances. |
| **Monthly Free Hours** | 750 free instance hours per month per account. | Sufficient for running one active service throughout the month. |

---

## 6. Inspecting Deployment Logs & Troubleshooting

If deployment encounters issues:
1. Go to your Render Dashboard &rarr; Click **loan-default-risk-prediction-ro68** &rarr; **Logs**.
2. **Build Failures:** Check if `pip install` failed. Verify `requirements.txt` does not contain conflicting packages.
3. **Out-Of-Memory (OOM):** If logs show `Container killed by OOM killer`, verify `--workers 1` is in your start command.
4. **Port Binding Error:** If logs show `Failed to bind to $PORT`, verify `--bind 0.0.0.0:$PORT` is set.
5. **Health Check Timeout:** Verify that `app.py` exposes `/health` and that model files in `Models/` exist in GitHub.

---

*Manual maintained by S Sreeram Ganesh. Last verified October 18, 2026.*
