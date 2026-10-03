import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ====================================================
# Configuration and Path Setup
# ====================================================
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "Models"
IMAGES_DIR = BASE_DIR / "src" / "images"

# Load Trained Model and Preprocessing Artifacts
print("Loading model artifacts...")
try:
    model = joblib.load(MODELS_DIR / "loan_prediction.pkl")
    feature_encoders = joblib.load(MODELS_DIR / "feature_encoders.pkl")
    target_encoder = joblib.load(MODELS_DIR / "target_encoder.pkl")
    print("All model artifacts loaded successfully!")
except Exception as e:
    print(f"Error loading model artifacts: {e}")
    model = None
    feature_encoders = {}
    target_encoder = None

# Expected 8 features in strict order matching model training
FEATURE_COLUMNS = [
    "loan_amount",
    "installment",
    "int_rate",
    "annual_income",
    "dti",
    "application_type",
    "verification_status",
    "home_ownership"
]

# Chart catalog with titles and descriptions
CHART_CATALOG = [
    {
        "id": "model_performance",
        "category": "performance",
        "filename": "Model_Performance_Comparison.png",
        "title": "Overall Model Performance Comparison",
        "subtitle": "Decision Tree vs Random Forest across 6 core metrics",
        "insight": "Random Forest outperforms Decision Tree on Balanced Accuracy (+4.0%) and Macro F1-Score (+4.7%), proving superior fairness across minority and majority classes."
    },
    {
        "id": "confusion_matrices",
        "category": "matrices",
        "filename": "Model_Comparison_Confusion_Matrices.png",
        "title": "Normalized Confusion Matrix Comparison",
        "subtitle": "True detection rates (Recall) per class with business labels",
        "insight": "Random Forest catches 20.1% of actual loan defaulters (Charged Off), more than doubling Decision Tree's 9.0% detection rate."
    },
    {
        "id": "class_performance",
        "category": "performance",
        "filename": "Class_Performance_Comparison.png",
        "title": "Class-Specific Recall & F1-Score",
        "subtitle": "Breakdown for Charged Off (Risk), Current, and Fully Paid",
        "insight": "High-risk loan default prediction is heavily improved under Random Forest (F1: 20.9% vs 12.9%), mitigating severe lender loss."
    },
    {
        "id": "feature_importance",
        "category": "features",
        "filename": "Feature_Importance_Comparison.png",
        "title": "Dual Feature Importance Comparison",
        "subtitle": "How each model weights borrower financial indicators",
        "insight": "Interest rate, installment amount, and DTI ratio are the top 3 drivers of default prediction across both models."
    },
    {
        "id": "target_distribution",
        "category": "dataset",
        "filename": "Target_Class_Distribution.png",
        "title": "Dataset Class Distribution & Imbalance",
        "subtitle": "Overview of 38,574 historical loan outcomes",
        "insight": "83.3% of applicants are Fully Paid while only 13.8% are Charged Off, explaining why raw accuracy alone is a deceptive metric."
    }
]


# ====================================================
# Routes
# ====================================================

@app.route("/")
def index():
    """Serves the main application dashboard."""
    options = {}
    if feature_encoders:
        for col, enc in feature_encoders.items():
            options[col] = list(enc.classes_)
    else:
        options = {
            "application_type": ["INDIVIDUAL"],
            "verification_status": ["Not Verified", "Source Verified", "Verified"],
            "home_ownership": ["MORTGAGE", "RENT", "OWN", "OTHER", "NONE"]
        }

    return render_template(
        "index.html",
        options=options,
        charts=CHART_CATALOG
    )


@app.route("/predict", methods=["POST"])
def predict():
    """API endpoint to predict loan default risk and verification decision."""
    if model is None or target_encoder is None:
        return jsonify({
            "status": "error",
            "message": "Model artifacts not loaded. Please ensure models are trained and saved in Models/."
        }), 500

    try:
        data = request.get_json(force=True)

        # 1. Parse and validate numeric features
        try:
            loan_amount = float(data.get("loan_amount", 0))
            installment = float(data.get("installment", 0))
            int_rate = float(data.get("int_rate", 0))
            annual_income = float(data.get("annual_income", 0))
            dti = float(data.get("dti", 0))
        except (ValueError, TypeError) as e:
            return jsonify({
                "status": "error",
                "message": f"Invalid numeric input provided: {e}"
            }), 400

        # Input sanitization
        if loan_amount <= 0 or annual_income <= 0:
            return jsonify({
                "status": "error",
                "message": "Loan Amount and Annual Income must be greater than zero."
            }), 400

        # Convert percentages if user entered 12.5 instead of 0.125
        if int_rate > 1.0:
            int_rate_normalized = int_rate / 100.0
        else:
            int_rate_normalized = int_rate

        if dti > 1.0:
            dti_normalized = dti / 100.0
        else:
            dti_normalized = dti

        # 2. Parse and encode categorical features
        app_type = str(data.get("application_type", "INDIVIDUAL")).strip()
        ver_status = str(data.get("verification_status", "Not Verified")).strip()
        home_own = str(data.get("home_ownership", "RENT")).strip()

        def safe_encode(col_name, val):
            if col_name in feature_encoders:
                enc = feature_encoders[col_name]
                if val in enc.classes_:
                    return int(enc.transform([val])[0])
                else:
                    return 0
            return 0

        app_type_enc = safe_encode("application_type", app_type)
        ver_status_enc = safe_encode("verification_status", ver_status)
        home_own_enc = safe_encode("home_ownership", home_own)

        # 3. Construct DataFrame matching model columns exactly
        input_data = {
            "loan_amount": [loan_amount],
            "installment": [installment],
            "int_rate": [int_rate_normalized],
            "annual_income": [annual_income],
            "dti": [dti_normalized],
            "application_type": [app_type_enc],
            "verification_status": [ver_status_enc],
            "home_ownership": [home_own_enc]
        }
        input_df = pd.DataFrame(input_data)[FEATURE_COLUMNS]

        # 4. Model Prediction
        pred_idx = model.predict(input_df)[0]
        prediction_label = target_encoder.inverse_transform([pred_idx])[0]

        # Calculate class probabilities
        probabilities = {}
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_df)[0]
            for cls_name, prob in zip(target_encoder.classes_, probs):
                probabilities[cls_name] = round(float(prob) * 100, 2)
        else:
            # Fallback if probability not supported
            probabilities = {
                "Fully Paid": 85.0 if prediction_label == "Fully Paid" else 15.0,
                "Charged Off": 85.0 if prediction_label == "Charged Off" else 15.0,
                "Current": 0.0
            }

        # 5. Risk Assessment Logic
        default_prob = probabilities.get("Charged Off", 0.0)
        current_prob = probabilities.get("Current", 0.0)
        fully_paid_prob = probabilities.get("Fully Paid", 0.0)

        # Financial health metrics
        monthly_burden = (installment * 12 / annual_income * 100) if annual_income > 0 else 0
        loan_to_income = (loan_amount / annual_income * 100) if annual_income > 0 else 0

        # Decision Matrix
        if prediction_label == "Fully Paid" and default_prob < 30.0:
            decision = "VERIFIED & APPROVED"
            decision_badge = "success"
            risk_tier = "Low Risk"
            recommendation = "Applicant displays a strong debt-to-income profile with minimal risk of charge-off. Recommended for automatic verification and loan origination."
        elif prediction_label == "Charged Off" or default_prob >= 35.0:
            decision = "REJECTED (HIGH DEFAULT RISK)"
            decision_badge = "danger"
            risk_tier = "High Risk"
            recommendation = "High probability of default detected. Key drivers include high debt-to-income burden and elevated interest tier. Verification rejected."
        else:
            decision = "MANUAL UNDERWRITER REVIEW"
            decision_badge = "warning"
            risk_tier = "Moderate Risk"
            recommendation = "Applicant falls into a borderline risk bracket. Secondary income verification, credit pull, and collateral assessment recommended before disbursement."

        return jsonify({
            "status": "success",
            "decision": decision,
            "decision_badge": decision_badge,
            "risk_tier": risk_tier,
            "predicted_class": prediction_label,
            "default_risk_percentage": default_prob,
            "recommendation": recommendation,
            "probabilities": {
                "Fully Paid": fully_paid_prob,
                "Charged Off": default_prob,
                "Current": current_prob
            },
            "financial_summary": {
                "loan_amount": f"${loan_amount:,.2f}",
                "annual_income": f"${annual_income:,.2f}",
                "installment": f"${installment:,.2f}/mo",
                "interest_rate": f"{int_rate_normalized * 100:.2f}%",
                "dti_ratio": f"{dti_normalized * 100:.1f}%",
                "monthly_burden_pct": f"{monthly_burden:.1f}%",
                "loan_to_income_pct": f"{loan_to_income:.1f}%"
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server encountered an error during prediction: {str(e)}"
        }), 500


@app.route("/charts/<path:filename>")
def serve_chart(filename):
    """Serves generated chart PNGs from src/images/."""
    return send_from_directory(IMAGES_DIR, filename)


@app.route("/api/metrics")
def get_metrics():
    """Returns static model comparison summary metrics."""
    return jsonify({
        "models": {
            "Decision Tree": {
                "accuracy": 80.39,
                "balanced_accuracy": 36.07,
                "macro_f1": 36.27,
                "defaulter_recall": 9.00
            },
            "Random Forest": {
                "accuracy": 76.59,
                "balanced_accuracy": 40.09,
                "macro_f1": 41.00,
                "defaulter_recall": 20.10
            }
        },
        "winner": "Random Forest",
        "winner_reason": "Random Forest provides +4.73% higher Macro F1 and 2.2x higher defaulter detection rate (20.1% vs 9.0%), mitigating significant credit default losses."
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n=================================================")
    print(f" Loan Verification & Prediction Server Active")
    print(f" Open your browser: http://127.0.0.1:{port}")
    print(f"=================================================\n")
    app.run(debug=True, host="127.0.0.1", port=port)
