# ml/src/integrate_with_data.py
import pandas as pd
from tax_recommendation_engine import generate_recommendations

df = pd.read_csv("../data/raw/financial_data.csv")

results = []
for _, row in df.head(10).iterrows():  # first 10 rows
    user = {
        "gross_income": row.get("annual_income", 0),
        "age": row.get("age", 30),
        "risk_appetite": "medium",
        # map more columns...
    }
    rec = generate_recommendations(user)
    results.append(rec)

print(f"Processed {len(results)} users")
print(results[0])  # see first one