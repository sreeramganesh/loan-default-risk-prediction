# 🛡️ LoanGuard AI — Credit Risk Analysis & Loan Default Prediction (Data Science & ML)

[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An end-to-end **Data Science & Applied Machine Learning** platform that combines exploratory credit risk analysis, feature engineering, and predictive modeling with a real-time Streamlit underwriting portal.

---

## 🌟 Key Features

- **⚡ Real-Time Risk Assessment**: Instant inference with automated credit risk tier classification (Prime, Near-Prime, Subprime).
- **🎨 High-End Fintech UI**: Designed with a sleek dark-mode interface, responsive CSS design tokens, and modular typography.
- **👥 Interactive Test Profiles**: One-click preset profiles (Prime, Moderate, Subprime) for instantaneous model testing.
- **📊 Feature Importance & Explainability**: In-depth visualization of key drivers influencing approval and default risk (DTI, annual income, interest rates, installment terms).
- **🔄 Dual App Architecture**:
  - **Streamlit Frontend** (`streamlit_app.py`): Interactive decisioning portal.
  - **Flask REST API** (`app.py`): Microservice ready for programmatic scoring integrations.
- **☁️ Zero-Config Streamlit Cloud Deployment**: Ready out-of-the-box with `.streamlit/config.toml` and `.python-version`.

---

## 🏗️ Architecture & Model Features

The underlying machine learning model evaluates applicants across 8 core financial attributes:

| Feature | Description | Example / Range |
|---|---|---|
| `loan_amount` | Total principal requested | `$1,000 – $40,000` |
| `installment` | Monthly payment obligation | `$30.00 – $1,500.00` |
| `int_rate` | Annual interest rate | `5.0% – 30.0%` |
| `annual_income` | Self-reported verified annual earnings | `$10,000 – $250,000+` |
| `dti` | Debt-to-Income ratio | `0.0% – 45.0%` |
| `application_type` | Individual or Joint application | `INDIVIDUAL`, `JOINT` |
| `verification_status` | Income source verification status | `Verified`, `Source Verified`, `Not Verified` |
| `home_ownership` | Real estate tenure | `RENT`, `MORTGAGE`, `OWN` |

---

## 📁 Repository Structure

```text
loan-default-risk-prediction/
├── .streamlit/
│   └── config.toml             # Custom Streamlit server & theme settings
├── Models/
│   ├── loan_prediction.pkl     # Trained Random Forest / Ensemble model
│   ├── feature_encoders.pkl    # Preprocessing categorical encoders
│   └── target_encoder.pkl     # Target class label encoder
├── src/
│   ├── images/                 # Model evaluation charts & confusion matrices
│   ├── Loan_Prediction.py      # Data preprocessing, training & evaluation pipeline
│   ├── Random_Forest.py        # Random Forest model script
│   └── Decision tree.py        # Decision Tree comparison script
├── static/                     # Assets for Flask frontend
├── templates/                  # HTML templates for Flask interface
├── .gitignore                  # Git ignore rules for virtual environments
├── .python-version             # Python version pin for Streamlit Cloud (3.11)
├── app.py                      # Flask REST API server
├── requirements.txt            # Python dependencies
├── streamlit_app.py            # Main LoanGuard AI Streamlit Dashboard
└── README.md                   # Project documentation
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_USERNAME>/loan-default-risk-prediction.git
cd loan-default-risk-prediction
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.\.venv\Scripts\activate

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Portal
```bash
streamlit run streamlit_app.py
```
Open your browser at `http://localhost:8501`.

*(Optional)* To run the Flask service:
```bash
python app.py
```

---

## ☁️ Deploy to Streamlit Community Cloud (Free)

Deploying takes less than 2 minutes:

1. Push this repository to your GitHub account:
   ```bash
   git add .
   git commit -m "feat: complete LoanGuard AI app"
   git push -u origin main
   ```
2. Navigate to **[share.streamlit.io](https://share.streamlit.io)** and log in with GitHub.
3. Click **New app** and select:
   * **Repository:** `<YOUR_USERNAME>/<YOUR_REPO_NAME>`
   * **Branch:** `main`
   * **Main file path:** `streamlit_app.py`
4. Click **Deploy!**

Your app will build and go live at `https://<your-app-name>.streamlit.app`.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
