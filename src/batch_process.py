# ml/src/batch_process.py
import pandas as pd
from tax_recommendation_engine import generate_recommendations
import json

def batch_generate_recommendations(csv_path, output_path="processed_recommendations.json"):
    print("Loading dataset...")
    df = pd.read_csv(csv_path)

    results = []

    for idx, row in df.iterrows():
        user = {
            "gross_income": float(row.get("gross_income", 0)),
            "age": int(row.get("age", 30)),
            "city_type": row.get("city_type", "metro"),
            "has_rent": bool(row.get("has_rent", False)),
            "monthly_rent": float(row.get("monthly_rent", 0)),
            "risk_appetite": row.get("risk_appetite", "medium"),
            "current_80c": float(row.get("current_80c", 0)),
            "current_80d": float(row.get("current_80d", 0))
            # Add more mappings if your CSV has different column names
        }

        try:
            rec = generate_recommendations(user)
            rec["user_index"] = idx
            results.append(rec)
            print(f"Processed user {idx+1}")
        except Exception as e:
            print(f"Error processing user {idx+1}: {e}")
            results.append({"user_index": idx, "error": str(e)})

    # Save results
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nProcessed {len(results)} users. Saved to {output_path}")

if __name__ == "__main__":
 batch_generate_recommendations(r"C:/Users/USER/OneDrive/Pictures/Desktop/ml/ml/data/raw/financial_data.csv")