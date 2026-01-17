# ml/api/app.py
import sys
import os

# Add the parent directory (ml/) to Python's search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from flask import Flask, request, jsonify
from src.tax_recommendation_engine import generate_recommendations

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)# ml/src/tax_recommendation_engine.py
