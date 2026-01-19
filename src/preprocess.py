import pandas as pd
from tax_recommendation_engine import generate_recommendations

df = pd.read_csv("../data/raw/financial_data.csv")

# Example: apply engine to first 5 rows (assuming columns exist)
for i in range(5):
    user = {
        "gross_income": df.iloc[i]["income"],
        "age": df.iloc[i]["age"],
        "risk_appetite": "medium",  # or map from data
        # add more mappings...
    }
    result = generate_recommendations(user)
    print(f"User {i+1}:", result["recommended_regime"], result["potential_savings"])