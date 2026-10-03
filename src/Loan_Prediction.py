import os
from pathlib import Path
import pandas as pd
import joblib

try:
    import matplotlib
    matplotlib.use("Agg")  # Non-interactive backend suitable for scripts/headless runs
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay
)

# ===========================
# Project Path Configuration
# ===========================
SRC_DIR = Path(__file__).resolve().parent
BASE_DIR = SRC_DIR.parent
DATA_DIR = BASE_DIR / "Data"
MODELS_DIR = BASE_DIR / "Models"
IMAGES_DIR = SRC_DIR / "images"

# Ensure output directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)


# ===========================
# Load Dataset
# ===========================
def load_data():
    print("\nLoading Dataset...")
    # Prefer Excel in DATA_DIR, otherwise fallback to CSV
    excel_path = DATA_DIR / "Loan_Data.xlsx"
    csv_path = DATA_DIR / "Loan_Data.csv"

    # Fallback to local script folder if not in Data/
    if not excel_path.exists():
        excel_path = SRC_DIR / "Loan_Data.xlsx"
    if not csv_path.exists():
        csv_path = SRC_DIR / "Loan_Data.csv"

    if excel_path.exists():
        try:
            print(f"Reading Excel dataset from: {excel_path}")
            fact = pd.read_excel(excel_path, sheet_name="Fact_Loan")
            employment = pd.read_excel(excel_path, sheet_name="Dim_Employment")
            purpose = pd.read_excel(excel_path, sheet_name="Dim_Purpose")
            credit = pd.read_excel(excel_path, sheet_name="Dim_Credit_Grade")
            term = pd.read_excel(excel_path, sheet_name="Dim_Term")
            geography = pd.read_excel(excel_path, sheet_name="Dim_Geography")
        except Exception as e:
            print(f"Failed to read Excel file '{excel_path}': {e}")
            print("Falling back to CSV if available.")
            if csv_path.exists():
                print(f"Reading CSV dataset from: {csv_path}")
                df = pd.read_csv(csv_path)
                fact = df
                employment = pd.DataFrame()
                purpose = pd.DataFrame()
                credit = pd.DataFrame()
                term = pd.DataFrame()
                geography = pd.DataFrame()
            else:
                raise
    else:
        # Fallback: try to read combined CSV
        if csv_path.exists():
            print(f"Reading CSV dataset from: {csv_path}")
            df = pd.read_csv(csv_path)
            fact = df
            employment = pd.DataFrame()
            purpose = pd.DataFrame()
            credit = pd.DataFrame()
            term = pd.DataFrame()
            geography = pd.DataFrame()
        else:
            raise FileNotFoundError(
                f"No dataset found. Checked '{excel_path}' and '{csv_path}'."
            )
    print("Dataset Loaded Successfully")

    return (
        fact,
        employment,
        purpose,
        credit,
        term,
        geography
    )


# ===========================
# Merge Dataset
# ===========================
def merge_data(
        fact,
        employment,
        purpose,
        credit,
        term,
        geography
):
    print("\nMerging Tables...")
    df = fact.copy()

    def _safe_merge(left, right, key):
        if right is None or right.empty:
            print(f"Skipping merge for '{key}' — right table empty.")
            return left

        if key not in left.columns:
            print(f"Skipping merge for '{key}' — key not in left dataframe.")
            return left

        if key not in right.columns:
            print(f"Skipping merge for '{key}' — key not in right dataframe.")
            return left

        return left.merge(right, on=key, how="left")

    df = _safe_merge(df, employment, "employment_key")
    df = _safe_merge(df, purpose, "purpose_key")
    df = _safe_merge(df, credit, "credit_key")
    df = _safe_merge(df, term, "term_key")
    df = _safe_merge(df, geography, "geography_key")
    print("Merge Completed")
    print(f"Dataset Shape : {df.shape}")

    return df


# ===========================
# Data Preprocessing
# ===========================
def preprocess_data(df):
    print("\nPreprocessing Dataset...")

    columns_to_drop = [
        "id",
        "borrower_key",
        "member_id",
        "employment_key",
        "purpose_key",
        "credit_key",
        "term_key",
        "geography_key",
        "issue_date",
        "last_credit_pull_date",
        "last_payment_date",
        "next_payment_date",
        # Dropping post-origination metric to prevent data leakage (unseen for new applicants):
        "total_payment"
    ]

    # Drop any unnamed columns created by trailing commas in CSV files
    unnamed_cols = [c for c in df.columns if c.startswith("Unnamed")]
    columns_to_drop.extend(unnamed_cols)

    cols_to_drop_present = [c for c in columns_to_drop if c in df.columns]
    df.drop(columns=cols_to_drop_present, inplace=True)

    # Fill Missing Values
    print(f"Missing Values:\n{df.isnull().sum()}")

    if "emp_title" in df.columns:
        df["emp_title"] = df["emp_title"].fillna("Unknown")
    else:
        print("Column 'emp_title' not found — skipping emp_title fill.")

    # Remove duplicate rows
    print(f"Duplicate Rows: {df.duplicated().sum()}")
    df.drop_duplicates(inplace=True)

    print("Preprocessing Completed")
    print(f"Final Dataset Shape : {df.shape}")

    return df


# ===========================
# Encode Features
# ===========================
def encode_features(df):
    print("\nEncoding Features...")

    X = df.drop("loan_status", axis=1)
    y = df["loan_status"]

    categorical_columns = [
        "application_type",
        "verification_status",
        "home_ownership",
        "emp_title",
        "emp_length",
        "purpose",
        "grade",
        "sub_grade",
        "term",
        "address_state"
    ]

    feature_encoders = {}

    present_categorical = [c for c in categorical_columns if c in X.columns]
    missing_categorical = [c for c in categorical_columns if c not in X.columns]

    if missing_categorical:
        print(f"Skipping encoding for missing categorical columns: {missing_categorical}")

    for column in present_categorical:
        # Fill missing values before encoding
        X[column] = X[column].fillna("Unknown")
        encoder = LabelEncoder()
        X[column] = encoder.fit_transform(X[column].astype(str))
        feature_encoders[column] = encoder

    # Encode Target
    target_encoder = LabelEncoder()
    y = target_encoder.fit_transform(y)

    print("Encoding Completed")

    return (
        X,
        y,
        feature_encoders,
        target_encoder
    )


# ===========================
# Split Dataset
# ===========================
def split_dataset(X, y):
    print("\nSplitting Dataset...")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    print("Training Samples :", len(X_train))
    print("Testing Samples  :", len(X_test))

    return (
        X_train, X_test, y_train, y_test
    )


# ===========================
# Train Decision Tree Model
# ===========================
def train_decision_tree(X_train, y_train):
    print("\nTraining Decision Tree Model...")

    dt_model = DecisionTreeClassifier(
        criterion="entropy",
        max_depth=12,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42
    )

    dt_model.fit(X_train, y_train)

    print("Decision Tree Training Completed.")

    return dt_model


# ===========================
# Train Random Forest Model
# ===========================
def train_random_forest(X_train, y_train):
    print("\nTraining Random Forest Model...")

    rf_model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    rf_model.fit(X_train, y_train)

    print("Random Forest Training Completed.")

    return rf_model


# ===========================
# Evaluate Model
# ===========================
def evaluate_model(model, X_test, y_test, model_name, class_names=None):
    prediction = model.predict(X_test)
    accuracy = accuracy_score(y_test, prediction)
    balanced_acc = balanced_accuracy_score(y_test, prediction)
    macro_precision = precision_score(y_test, prediction, average="macro", zero_division=0)
    macro_recall = recall_score(y_test, prediction, average="macro", zero_division=0)
    macro_f1 = f1_score(y_test, prediction, average="macro", zero_division=0)
    weighted_f1 = f1_score(y_test, prediction, average="weighted", zero_division=0)

    per_class_p, per_class_r, per_class_f1, _ = precision_recall_fscore_support(
        y_test, prediction, average=None, zero_division=0
    )

    print("\n" + "=" * 60)
    print(f"{model_name.upper()} RESULTS")
    print("=" * 60)
    print(f"Overall Accuracy       : {accuracy * 100:.2f}%")
    print(f"Balanced Accuracy      : {balanced_acc * 100:.2f}%")
    print(f"Macro Precision        : {macro_precision * 100:.2f}%")
    print(f"Macro Recall           : {macro_recall * 100:.2f}%")
    print(f"Macro F1-Score         : {macro_f1 * 100:.2f}%")
    print(f"Weighted F1-Score      : {weighted_f1 * 100:.2f}%")

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, prediction))

    print("\nClassification Report:")
    print(classification_report(y_test, prediction, target_names=class_names, zero_division=0))

    return {
        "model_name": model_name,
        "prediction": prediction,
        "accuracy": accuracy,
        "balanced_accuracy": balanced_acc,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_f1": weighted_f1,
        "per_class_precision": per_class_p,
        "per_class_recall": per_class_r,
        "per_class_f1": per_class_f1
    }


# ===========================
# Plot Confusion Matrix
# ===========================
def plot_confusion_matrix(model, X_test, y_test, model_name, class_names=None):
    if plt is None:
        print("matplotlib not available — skipping confusion matrix plot.")
        return

    plt.figure(figsize=(7, 6))

    display_title = model_name.replace("_", " ")
    cmap = "Blues" if "Decision" in model_name else "Greens"

    disp = ConfusionMatrixDisplay.from_estimator(
        model,
        X_test,
        y_test,
        display_labels=class_names,
        cmap=cmap,
        xticks_rotation=15
    )

    disp.ax_.set_title(f"{display_title} Confusion Matrix", fontsize=13, fontweight="bold", pad=10)
    plt.tight_layout()

    out_file = IMAGES_DIR / f"{model_name}_Confusion_Matrix.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved confusion matrix plot to: {out_file}")


# ===========================
# Plot Side-by-Side Confusion Matrices
# ===========================
def plot_side_by_side_confusion_matrices(dt_model, rf_model, X_test, y_test, class_names):
    if plt is None:
        print("matplotlib not available — skipping comparison confusion matrices.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    models_info = [
        (dt_model, "Decision Tree", "Blues", axes[0]),
        (rf_model, "Random Forest", "Greens", axes[1])
    ]

    for model, name, cmap, ax in models_info:
        ConfusionMatrixDisplay.from_estimator(
            model,
            X_test,
            y_test,
            display_labels=class_names,
            cmap=cmap,
            normalize="true",
            values_format=".1%",
            ax=ax
        )
        ax.set_title(f"{name} (Normalized Recall)", fontsize=12, fontweight="bold", pad=10)
        ax.tick_params(axis="x", rotation=15)

    plt.suptitle("Normalized Confusion Matrix Comparison (True Detection Rates)", fontsize=14, fontweight="bold", y=0.98)
    plt.tight_layout()

    out_file = IMAGES_DIR / "Model_Comparison_Confusion_Matrices.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved side-by-side confusion matrix plot to: {out_file}")


# ===========================
# Plot Model Comparison Metrics
# ===========================
def plot_model_comparison_metrics(dt_metrics, rf_metrics):
    if plt is None:
        print("matplotlib not available — skipping model comparison metrics plot.")
        return

    metric_labels = [
        "Accuracy",
        "Balanced\nAccuracy",
        "Macro\nPrecision",
        "Macro\nRecall",
        "Macro\nF1-Score",
        "Weighted\nF1-Score"
    ]

    dt_values = [
        dt_metrics["accuracy"] * 100,
        dt_metrics["balanced_accuracy"] * 100,
        dt_metrics["macro_precision"] * 100,
        dt_metrics["macro_recall"] * 100,
        dt_metrics["macro_f1"] * 100,
        dt_metrics["weighted_f1"] * 100
    ]

    rf_values = [
        rf_metrics["accuracy"] * 100,
        rf_metrics["balanced_accuracy"] * 100,
        rf_metrics["macro_precision"] * 100,
        rf_metrics["macro_recall"] * 100,
        rf_metrics["macro_f1"] * 100,
        rf_metrics["weighted_f1"] * 100
    ]

    x = np.arange(len(metric_labels))
    width = 0.35

    plt.figure(figsize=(12, 6))
    ax = plt.subplot(111)

    rects1 = ax.bar(x - width/2, dt_values, width, label="Decision Tree", color="#2b5c8f", edgecolor="black", alpha=0.9)
    rects2 = ax.bar(x + width/2, rf_values, width, label="Random Forest", color="#28a745", edgecolor="black", alpha=0.9)

    ax.set_ylabel("Score (%)", fontsize=11, fontweight="bold")
    ax.set_title("Overall Model Performance Comparison: Decision Tree vs Random Forest", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(metric_labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 105)
    ax.legend(fontsize=11, frameon=True, loc="upper right")
    ax.grid(axis="y", linestyle="--", alpha=0.4)

    for rect in rects1:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#1c3d5a")

    for rect in rects2:
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#19692c")

    plt.tight_layout()
    out_file = IMAGES_DIR / "Model_Performance_Comparison.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved model performance comparison plot to: {out_file}")


# ===========================
# Plot Per-Class Performance Comparison
# ===========================
def plot_class_performance_comparison(dt_metrics, rf_metrics, class_names):
    if plt is None:
        print("matplotlib not available — skipping per-class performance plot.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    x = np.arange(len(class_names))
    width = 0.35

    # Subplot 1: Recall per class
    dt_recall = [r * 100 for r in dt_metrics["per_class_recall"]]
    rf_recall = [r * 100 for r in rf_metrics["per_class_recall"]]

    r1 = ax1.bar(x - width/2, dt_recall, width, label="Decision Tree", color="#2b5c8f", edgecolor="black", alpha=0.9)
    r2 = ax1.bar(x + width/2, rf_recall, width, label="Random Forest", color="#28a745", edgecolor="black", alpha=0.9)

    ax1.set_ylabel("Recall (%)", fontsize=11, fontweight="bold")
    ax1.set_title("Per-Class Recall (Detection Rate)\n*Critical for detecting Charged Off defaulters*", fontsize=11, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(class_names, fontsize=10, fontweight="bold")
    ax1.set_ylim(0, 110)
    ax1.legend(fontsize=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    for r in r1:
        h = r.get_height()
        ax1.annotate(f"{h:.1f}%", (r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for r in r2:
        h = r.get_height()
        ax1.annotate(f"{h:.1f}%", (r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    # Subplot 2: F1-score per class
    dt_f1 = [f * 100 for f in dt_metrics["per_class_f1"]]
    rf_f1 = [f * 100 for f in rf_metrics["per_class_f1"]]

    f1 = ax2.bar(x - width/2, dt_f1, width, label="Decision Tree", color="#2b5c8f", edgecolor="black", alpha=0.9)
    f2 = ax2.bar(x + width/2, rf_f1, width, label="Random Forest", color="#28a745", edgecolor="black", alpha=0.9)

    ax2.set_ylabel("F1-Score (%)", fontsize=11, fontweight="bold")
    ax2.set_title("Per-Class F1-Score\n*Harmonic Balance of Precision & Recall*", fontsize=11, fontweight="bold")
    ax2.set_xticks(x)
    ax2.set_xticklabels(class_names, fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 110)
    ax2.legend(fontsize=10)
    ax2.grid(axis="y", linestyle="--", alpha=0.4)

    for r in f1:
        h = r.get_height()
        ax2.annotate(f"{h:.1f}%", (r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for r in f2:
        h = r.get_height()
        ax2.annotate(f"{h:.1f}%", (r.get_x() + r.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.suptitle("Class-Specific Model Comparison", fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()

    out_file = IMAGES_DIR / "Class_Performance_Comparison.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved class performance comparison plot to: {out_file}")


# ===========================
# Plot Dual Feature Importance Comparison
# ===========================
def plot_feature_importance_comparison(dt_model, rf_model, X):
    if plt is None:
        print("matplotlib not available — skipping feature importance comparison.")
        return

    features = list(X.columns)
    dt_imp = dt_model.feature_importances_ if hasattr(dt_model, "feature_importances_") else np.zeros(len(features))
    rf_imp = rf_model.feature_importances_ if hasattr(rf_model, "feature_importances_") else np.zeros(len(features))

    df_imp = pd.DataFrame({
        "Feature": features,
        "Decision_Tree": dt_imp,
        "Random_Forest": rf_imp
    })

    df_imp["Mean_Importance"] = (df_imp["Decision_Tree"] + df_imp["Random_Forest"]) / 2
    df_imp = df_imp.sort_values(by="Mean_Importance", ascending=True)

    y = np.arange(len(df_imp))
    height = 0.38

    plt.figure(figsize=(11, 7))
    plt.barh(y - height/2, df_imp["Decision_Tree"], height, label="Decision Tree", color="#2b5c8f", alpha=0.9, edgecolor="black")
    plt.barh(y + height/2, df_imp["Random_Forest"], height, label="Random Forest", color="#28a745", alpha=0.9, edgecolor="black")

    plt.yticks(y, df_imp["Feature"], fontsize=10, fontweight="bold")
    plt.xlabel("Importance Score", fontsize=11, fontweight="bold")
    plt.title("Feature Importance Comparison: Decision Tree vs Random Forest", fontsize=13, fontweight="bold", pad=15)
    plt.legend(fontsize=11, loc="lower right", frameon=True)
    plt.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()

    out_file = IMAGES_DIR / "Feature_Importance_Comparison.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved feature importance comparison plot to: {out_file}")


# ===========================
# Plot Target Class Distribution
# ===========================
def plot_target_distribution(df, target_col="loan_status"):
    if plt is None:
        print("matplotlib not available — skipping target distribution plot.")
        return

    if target_col not in df.columns:
        print(f"Column '{target_col}' not found — skipping target distribution plot.")
        return

    counts = df[target_col].value_counts()
    percentages = df[target_col].value_counts(normalize=True) * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    colors = ["#2ecc71", "#e74c3c", "#f39c12"]

    # Bar chart
    bars = ax1.bar(counts.index, counts.values, color=colors, edgecolor="black", alpha=0.85)
    ax1.set_ylabel("Number of Applicants", fontsize=11, fontweight="bold")
    ax1.set_title("Applicant Count by Status", fontsize=12, fontweight="bold")
    ax1.grid(axis="y", linestyle="--", alpha=0.4)
    for bar in bars:
        h = bar.get_height()
        ax1.annotate(f"{h:,}", (bar.get_x() + bar.get_width() / 2, h),
                     xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                     fontsize=9.5, fontweight="bold")

    # Donut chart
    ax2.pie(
        percentages.values,
        labels=percentages.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        wedgeprops=dict(width=0.4, edgecolor="white", linewidth=2)
    )
    ax2.set_title("Dataset Class Share (% Imbalance)", fontsize=12, fontweight="bold")

    plt.suptitle("Loan Status Class Distribution (Imbalance Overview)", fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()

    out_file = IMAGES_DIR / "Target_Class_Distribution.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved target distribution plot to: {out_file}")


# ===========================
# Compare Models
# ===========================
def compare_models(dt_metrics, rf_metrics):
    print("\n" + "=" * 68)
    print("MODEL PERFORMANCE COMPARISON MATRIX")
    print("=" * 68)

    headers = f"{'Metric':<24} | {'Decision Tree':<15} | {'Random Forest':<15} | {'Difference':<10}"
    print(headers)
    print("-" * 68)

    metrics_to_show = [
        ("Accuracy", "accuracy"),
        ("Balanced Accuracy", "balanced_accuracy"),
        ("Macro Precision", "macro_precision"),
        ("Macro Recall", "macro_recall"),
        ("Macro F1-Score", "macro_f1"),
        ("Weighted F1-Score", "weighted_f1")
    ]

    for label, key in metrics_to_show:
        dt_val = dt_metrics[key] * 100
        rf_val = rf_metrics[key] * 100
        diff = rf_val - dt_val
        winner = "RF" if diff > 0 else ("DT" if diff < 0 else "Tie")
        diff_str = f"{diff:+.2f}% ({winner})"
        print(f"{label:<24} | {dt_val:>13.2f}% | {rf_val:>13.2f}% | {diff_str:>10}")

    print("=" * 68)

    print("\n[EVALUATION INSIGHT]")
    print("Due to severe class imbalance, raw Accuracy is dominated by the majority class.")
    print("Macro F1-Score and Balanced Accuracy reflect true ability to detect minority defaulters.")

    # Selection decision: prioritize balanced detection (Macro F1) over raw accuracy
    if rf_metrics["macro_f1"] > dt_metrics["macro_f1"]:
        best_model_name = "Random Forest"
        print(f"\nWinning Model (by Macro F1): Random Forest ({rf_metrics['macro_f1']*100:.2f}%)")
    elif dt_metrics["macro_f1"] > rf_metrics["macro_f1"]:
        best_model_name = "Decision Tree"
        print(f"\nWinning Model (by Macro F1): Decision Tree ({dt_metrics['macro_f1']*100:.2f}%)")
    else:
        best_model_name = "Random Forest"
        print("\nWinning Model: Random Forest (Tie-break)")

    return best_model_name


# ===========================
# Feature Importance
# ===========================
def display_feature_importance(model, X):
    if not hasattr(model, "feature_importances_"):
        print("Model does not provide feature importances.")
        return None

    importance = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_
    })

    importance = importance.sort_values(
        by="Importance",
        ascending=True
    )

    print("\nFeature Importance:")
    print(importance)

    if plt is None:
        print("matplotlib not available — skipping feature importance plot.")
        return importance

    plt.figure(figsize=(10, 7))
    plt.barh(
        importance["Feature"],
        importance["Importance"],
        color="#2b5c8f",
        edgecolor="black"
    )
    plt.xlabel("Importance", fontsize=11, fontweight="bold")
    plt.ylabel("Features", fontsize=11, fontweight="bold")
    plt.title("Winning Model Feature Importance", fontsize=13, fontweight="bold", pad=12)
    plt.grid(axis="x", linestyle="--", alpha=0.4)
    plt.tight_layout()

    out_file = IMAGES_DIR / "Feature_Importance.png"
    plt.savefig(out_file, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved feature importance plot to: {out_file}")

    return importance


# ===========================
# Save Model Artifacts
# ===========================
def save_model(model, filename="loan_prediction.pkl"):
    filepath = MODELS_DIR / filename
    joblib.dump(model, filepath)
    print(f"\nModel saved successfully as: '{filepath}'")


def save_feature_encoders(encoders, filename="feature_encoders.pkl"):
    filepath = MODELS_DIR / filename
    joblib.dump(encoders, filepath)
    print(f"Feature encoders saved successfully as: '{filepath}'")


def save_target_encoder(target_encoder, filename="target_encoder.pkl"):
    filepath = MODELS_DIR / filename
    joblib.dump(target_encoder, filepath)
    print(f"Target encoder saved successfully as: '{filepath}'")


# ============================================================
# Main Function
# ============================================================
def main():
    print("=" * 60)
    print("LOAN VERIFICATION PREDICTION SYSTEM")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Load Dataset
    # --------------------------------------------------------
    fact, employment, purpose, credit, term, geography = load_data()

    # --------------------------------------------------------
    # 2. Merge Tables
    # --------------------------------------------------------
    df = merge_data(
        fact,
        employment,
        purpose,
        credit,
        term,
        geography
    )

    # --------------------------------------------------------
    # 3. Data Preprocessing
    # --------------------------------------------------------
    df = preprocess_data(df)

    # Generate Class Distribution Plot
    plot_target_distribution(df, "loan_status")

    # --------------------------------------------------------
    # 4. Feature Encoding
    # --------------------------------------------------------
    X, y, feature_encoders, target_encoder = encode_features(df)
    class_names = [str(c) for c in target_encoder.classes_]

    # --------------------------------------------------------
    # 5. Split Dataset
    # --------------------------------------------------------
    X_train, X_test, y_train, y_test = split_dataset(X, y)

    # --------------------------------------------------------
    # 6. Train Models
    # --------------------------------------------------------
    dt_model = train_decision_tree(
        X_train,
        y_train
    )

    rf_model = train_random_forest(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # 7. Evaluate Models with Comprehensive Metrics
    # --------------------------------------------------------
    dt_metrics = evaluate_model(
        dt_model,
        X_test,
        y_test,
        "Decision Tree",
        class_names=class_names
    )

    rf_metrics = evaluate_model(
        rf_model,
        X_test,
        y_test,
        "Random Forest",
        class_names=class_names
    )

    # --------------------------------------------------------
    # 8. Generate Visualizations (Confusion Matrices & Comparisons)
    # --------------------------------------------------------
    # Individual confusion matrices with class labels
    plot_confusion_matrix(
        dt_model,
        X_test,
        y_test,
        "Decision_Tree",
        class_names=class_names
    )

    plot_confusion_matrix(
        rf_model,
        X_test,
        y_test,
        "Random_Forest",
        class_names=class_names
    )

    # Side-by-side normalized confusion matrices
    plot_side_by_side_confusion_matrices(
        dt_model,
        rf_model,
        X_test,
        y_test,
        class_names=class_names
    )

    # Overall performance comparison bar chart
    plot_model_comparison_metrics(
        dt_metrics,
        rf_metrics
    )

    # Per-class detection and F1 comparison
    plot_class_performance_comparison(
        dt_metrics,
        rf_metrics,
        class_names=class_names
    )

    # Dual feature importance comparison
    plot_feature_importance_comparison(
        dt_model,
        rf_model,
        X
    )

    # --------------------------------------------------------
    # 9. Compare Models & Save Winning Model
    # --------------------------------------------------------
    best_model_name = compare_models(
        dt_metrics,
        rf_metrics
    )

    winning_model = rf_model if best_model_name == "Random Forest" else dt_model

    display_feature_importance(
        winning_model,
        X
    )

    save_model(
        winning_model,
        "loan_prediction.pkl"
    )

    # --------------------------------------------------------
    # 10. Save Encoders
    # --------------------------------------------------------
    save_feature_encoders(
        feature_encoders
    )

    save_target_encoder(
        target_encoder
    )

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------
    print("\n" + "=" * 60)
    print("PROJECT EXECUTED SUCCESSFULLY")
    print("=" * 60)


# ============================================================
# Run Program
# ============================================================
if __name__ == "__main__":
    main()