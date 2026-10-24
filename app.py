import os
from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from report_generator import (
    validate_and_assess,
    build_report_data,
    generate_excel_report,
    generate_csv_report
)

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
        try:
            data = request.get_json(force=True) if (request.is_json or request.data) else {}
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Malformed or invalid JSON payload received."
            }), 400

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Request payload must be a JSON object."
            }), 400

        assessment = validate_and_assess(data, model, target_encoder, feature_encoders, FEATURE_COLUMNS)
        report_meta = build_report_data(
            assessment,
            custom_report_id=data.get("report_id"),
            custom_timestamp=data.get("timestamp")
        )

        return jsonify({
            "status": "success",
            "report_id": report_meta["report_id"],
            "timestamp": report_meta["timestamp"],
            "decision": assessment["decision"],
            "decision_badge": assessment["decision_badge"],
            "risk_tier": assessment["risk_tier"],
            "predicted_class": assessment["predicted_class"],
            "default_risk_percentage": assessment["default_risk_percentage"],
            "recommendation": assessment["recommendation"],
            "probabilities": {
                "Fully Paid": assessment["fully_paid_percentage"],
                "Charged Off": assessment["default_risk_percentage"],
                "Current": assessment["current_percentage"]
            },
            "financial_summary": {
                "loan_amount": f"${assessment['loan_amount']:,.2f}",
                "annual_income": f"${assessment['annual_income']:,.2f}",
                "installment": f"${assessment['installment']:,.2f}/mo",
                "interest_rate": f"{assessment['int_rate_pct']:.2f}%",
                "dti_ratio": f"{assessment['dti_pct']:.1f}%",
                "monthly_burden_pct": f"{assessment['monthly_burden_pct']:.1f}%",
                "loan_to_income_pct": f"{assessment['loan_to_income_pct']:.1f}%"
            }
        })

    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Server encountered an error during prediction: {str(e)}"
        }), 500


@app.route("/api/reports/excel", methods=["POST"])
def export_excel_report():
    """Generates and downloads an audit-ready 3-sheet Excel report (.xlsx)."""
    if model is None or target_encoder is None:
        return jsonify({
            "status": "error",
            "message": "Model artifacts not loaded. Please ensure models are trained and saved in Models/."
        }), 500

    try:
        try:
            data = request.get_json(force=True) if (request.is_json or request.data) else {}
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Malformed or invalid JSON payload received."
            }), 400

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Request payload must be a JSON object."
            }), 400

        assessment = validate_and_assess(data, model, target_encoder, feature_encoders, FEATURE_COLUMNS)
        report_data = build_report_data(
            assessment,
            custom_report_id=data.get("report_id"),
            custom_timestamp=data.get("timestamp")
        )
        excel_buffer = generate_excel_report(report_data)
        safe_filename = f"LoanGuard_AI_Assessment_{report_data['report_id']}.xlsx"

        return send_file(
            excel_buffer,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=safe_filename
        )

    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Report generation failed: {str(e)}"
        }), 500


@app.route("/api/reports/csv", methods=["POST"])
def export_csv_report():
    """Generates and downloads an audit-ready 2-column CSV report (.csv)."""
    if model is None or target_encoder is None:
        return jsonify({
            "status": "error",
            "message": "Model artifacts not loaded. Please ensure models are trained and saved in Models/."
        }), 500

    try:
        try:
            data = request.get_json(force=True) if (request.is_json or request.data) else {}
        except Exception:
            return jsonify({
                "status": "error",
                "message": "Malformed or invalid JSON payload received."
            }), 400

        if not isinstance(data, dict):
            return jsonify({
                "status": "error",
                "message": "Request payload must be a JSON object."
            }), 400

        assessment = validate_and_assess(data, model, target_encoder, feature_encoders, FEATURE_COLUMNS)
        report_data = build_report_data(
            assessment,
            custom_report_id=data.get("report_id"),
            custom_timestamp=data.get("timestamp")
        )
        csv_buffer = generate_csv_report(report_data)
        safe_filename = f"LoanGuard_AI_Assessment_{report_data['report_id']}.csv"

        return send_file(
            csv_buffer,
            mimetype="text/csv; charset=utf-8",
            as_attachment=True,
            download_name=safe_filename
        )

    except ValueError as ve:
        return jsonify({
            "status": "error",
            "message": str(ve)
        }), 400
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Report generation failed: {str(e)}"
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


@app.route("/health")
def health():
    """Health check endpoint for Render/cloud deployment monitoring."""
    is_healthy = model is not None and target_encoder is not None
    return jsonify({
        "status": "healthy" if is_healthy else "degraded",
        "service": "LoanGuard AI Flask Service",
        "model_loaded": is_healthy
    }), 200 if is_healthy else 503


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() in ("true", "1")
    print(f"\n=================================================")
    print(f" Loan Verification & Prediction Server Active")
    print(f" Listening on http://0.0.0.0:{port} (local: http://127.0.0.1:{port})")
    print(f" Debug mode: {debug_mode}")
    print(f"=================================================\n")
    app.run(debug=debug_mode, host="0.0.0.0", port=port)

