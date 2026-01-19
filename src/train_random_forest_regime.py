# ml/src/train_random_forest_regime.py
import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def load_processed_data():
    json_path = "processed_recommendations.json"
    print("Loading data from:", json_path)
    
    if not os.path.exists(json_path):
        print("Error: File not found! Run batch_process.py first.")
        return None

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    rows = []
    for entry in data:
        if "error" in entry:
            continue

        user = entry.get("original_row", entry)  # fallback if no original_row

        row = {
            "gross_income": float(user.get("gross_income", 0)),
            "age": float(user.get("age", 30)),
            "city_type": 1 if user.get("city_type", "metro") == "metro" else 0,
            "has_rent": int(user.get("has_rent", False)),
            "monthly_rent": float(user.get("monthly_rent", 0)),
            "current_80c": float(user.get("current_80c", 0)),
            "current_80d": float(user.get("current_80d", 0)),
            # STRONG FEATURES - these will make accuracy much higher
            "tax_new": float(entry.get("tax_new", 0)),
            "tax_old": float(entry.get("tax_old", 0)),
            "savings_if_new": float(entry.get("potential_savings", 0)),
            # Target
            "target": 1 if entry["recommended_regime"] == "new" else 0
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    print(f"Loaded {len(df)} users")

    print("\nClass distribution:")
    print(df["target"].value_counts(normalize=True).mul(100).round(2).astype(str) + " %")
    print("0 = Old Regime | 1 = New Regime\n")

    return df


def train_model():
    df = load_processed_data()
    if df is None:
        return

    features = [
        "gross_income", "age", "city_type", "has_rent", "monthly_rent",
        "current_80c", "current_80d",
        "tax_new", "tax_old", "savings_if_new"  # These are the key ones!
    ]

    X = df[features].fillna(0)
    y = df["target"]

    if len(y.unique()) < 2:
        print("ERROR: Only one class. Need both regimes.")
        return

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"Training on {len(X_train)} | Testing on {len(X_test)}")

    model = RandomForestClassifier(
        n_estimators=200,          # more trees = better
        max_depth=12,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"\nAccuracy: {acc:.2%}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=["Old Regime", "New Regime"], zero_division=0))

    print("\nFeature Importance:")
    importances = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)
    print(importances.round(4))

    model_folder = "../models"
    os.makedirs(model_folder, exist_ok=True)
    model_path = os.path.join(model_folder, "random_forest_regime.pkl")
    joblib.dump(model, model_path)
    print(f"\nModel saved: {model_path}")


if __name__ == "__main__":
    train_model()