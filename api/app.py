# ml/api/app.py
import sys
import os
import json
import joblib
from flask import Flask, request, jsonify
import pandas as pd

# Make sure parent directory is in path (so src/ can be imported)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.tax_recommendation_engine import generate_recommendations

app = Flask(__name__)

# Load the trained Random Forest model once when server starts
MODEL_PATH = "../models/random_forest_regime.pkl"
try:
    regime_model = joblib.load(MODEL_PATH)
    print(f"ML model loaded successfully from {MODEL_PATH}")
except Exception as e:
    print(f"Warning: Could not load ML model - {e}")
    regime_model = None  # fallback if model not found

# Existing full recommendation endpoint (rule-based)
@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    if not data or "gross_income" not in data:
        return jsonify({"error": "Missing required field: gross_income"}), 400

    try:
        result = generate_recommendations(data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# New fast ML-only endpoint (predict regime using Random Forest)
@app.route('/predict_regime', methods=['POST'])
def predict_regime():
    if regime_model is None:
        return jsonify({"error": "ML model not loaded. Train and save the model first."}), 500

    data = request.get_json()
    if not data or "gross_income" not in data:
        return jsonify({"error": "Missing required field: gross_income"}), 400

    try:
        # Prepare input features (must match exactly what was used in training)
        features = [
            "gross_income", "age", "city_type", "has_rent", "monthly_rent",
            "current_80c", "current_80d"
        ]

        input_data = {
            "gross_income": float(data.get("gross_income", 0)),
            "age": float(data.get("age", 30)),
            "city_type": 1 if data.get("city_type", "metro") == "metro" else 0,
            "has_rent": int(data.get("has_rent", False)),
            "monthly_rent": float(data.get("monthly_rent", 0)),
            "current_80c": float(data.get("current_80c", 0)),
            "current_80d": float(data.get("current_80d", 0))
        }

        # Convert to DataFrame (single row)
        df_input = pd.DataFrame([input_data])

        # Predict
        prediction = regime_model.predict(df_input[features])[0]
        regime = "new" if prediction == 1 else "old"

        return jsonify({
            "predicted_regime": regime,
            "message": "Fast ML prediction (Random Forest)"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)