import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# Robust path handling - resolves relative to project root or current folder
BASE_DIR = Path(__file__).resolve().parent.parent
data_path = BASE_DIR / "Data" / "Loan_Data.csv"
if not data_path.exists():
    data_path = Path(__file__).resolve().parent / "Loan_Data.csv"

# Load dataset
df = pd.read_csv(data_path)

print("Dataset Preview:")
print(df.head())

# Check missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Features and target
# 'total_payment' is removed to avoid data leakage (post-origination repayment information).
# Using pre-origination applicant attributes: annual_income, loan_amount, and dti (debt-to-income ratio).
features = ['annual_income', 'loan_amount', 'dti']
x = df[features]
y = df['loan_status']

# Split data
x_train, x_test, y_train, y_test = train_test_split(
    x, y, test_size=0.25, random_state=42
)

# Create and train model
model = DecisionTreeClassifier(random_state=42)
model.fit(x_train, y_train)

# Prediction
y_pred = model.predict(x_test)

# Accuracy
accuracy = accuracy_score(y_test, y_pred)
print("\nAccuracy:", round(accuracy * 100, 2), "%")

# Confusion Matrix
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Classification Report
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Runtime Input
print("\nEnter New Customer Details")

annual_income = float(input("Enter Annual Income ($): "))
loan_amount = float(input("Enter Loan Amount ($): "))
dti = float(input("Enter Debt-to-Income (DTI) Ratio (e.g. 0.15 for 15%): "))

# Create New Customer Data
new_customer = pd.DataFrame(
    [[annual_income, loan_amount, dti]],
    columns=x.columns
)
prediction = model.predict(new_customer)
print("\nNew Customer Prediction:", prediction)

if prediction[0] == "Fully Paid":
    print("The loan is verified and approved.")
else:
    print("The loan is not verified and rejected.")