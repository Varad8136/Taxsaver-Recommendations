# ml/src/tax_recommendation_engine.py
# AI-Powered Tax Recommendation Engine (Rule-based + Scoring MVP)
# FY 2025-26 / AY 2026-27 rules

# ── TAX SLABS (New Regime - default since Budget 2025) ───────────────
NEW_REGIME_SLABS = [
    (400000, 0.00),      # 0 - 4L
    (800000, 0.05),      # 4L - 8L
    (1200000, 0.10),     # 8L - 12L
    (1600000, 0.15),     # 12L - 16L
    (2000000, 0.20),     # 16L - 20L
    (float('inf'), 0.30) # Above 20L
]

# Old Regime (below 60 years)
OLD_REGIME_SLABS_BELOW_60 = [
    (250000, 0.00),
    (500000, 0.05),
    (1000000, 0.20),
    (float('inf'), 0.30)
]

# Standard deduction (New Regime)
STANDARD_DEDUCTION_NEW = 75000

# Max deduction limits
MAX_LIMITS = {
    "80C": 150000,          # ELSS, PPF, NSC, 5yr FD, LIC, etc.
    "80CCD_1B": 50000,      # Extra NPS
    "80D_SELF_FAMILY": 25000,
    "80D_SENIOR_PARENTS": 50000,
    "CESS_RATE": 0.04       # Health & Education cess
}


def calculate_tax(taxable_income, slabs):
    """Calculate income tax + 4% cess"""
    tax = 0
    prev = 0

    for limit, rate in slabs:
        if taxable_income > limit:
            tax += (limit - prev) * rate
            prev = limit
        else:
            tax += (taxable_income - prev) * rate
            break

    cess = tax * MAX_LIMITS["CESS_RATE"]
    return round(tax + cess)


def generate_recommendations(user_profile):
    """
    Main function: Generate tax-saving recommendations
    Input: dict with user details
    Output: structured recommendation dictionary
    """
    gross = user_profile.get("gross_income", 0)
    age = user_profile.get("age", 30)
    current_80c = user_profile.get("current_80c", 0)
    current_80d = user_profile.get("current_80d", 0)
    risk_appetite = user_profile.get("risk_appetite", "medium")  # low / medium / high

    # ── 1. Calculate taxable income ─────────────────────────────────────
    taxable_new = max(0, gross - STANDARD_DEDUCTION_NEW)

    remaining_80c = max(0, MAX_LIMITS["80C"] - current_80c)
    remaining_nps_extra = MAX_LIMITS["80CCD_1B"]
    remaining_80d = MAX_LIMITS["80D_SELF_FAMILY"] - current_80d if current_80d < MAX_LIMITS["80D_SELF_FAMILY"] else 0

    taxable_old = max(0, gross - current_80c - remaining_nps_extra - remaining_80d)

    # ── 2. Tax liability both regimes ───────────────────────────────────
    tax_new = calculate_tax(taxable_new, NEW_REGIME_SLABS)
    tax_old = calculate_tax(taxable_old, OLD_REGIME_SLABS_BELOW_60)  # todo: senior slabs later

    savings_if_new = max(0, tax_old - tax_new)

    # ── 3. Regime recommendation ────────────────────────────────────────
    recommended_regime = "new"
    confidence = 0.85

    if savings_if_new > 25000:
        confidence = 0.92 if savings_if_new > 50000 else 0.88
    elif current_80c + remaining_nps_extra > 120000:
        recommended_regime = "old"
        confidence = 0.90

    # ── 4. Instrument scoring & recommendations ─────────────────────────
    instruments = []

    # ELSS (80C)
    if remaining_80c > 0:
        score = 90 if risk_appetite == "high" else 75 if risk_appetite == "medium" else 50
        amount = min(remaining_80c, 100000)  # suggest reasonable amount
        save = round(amount * 0.3)  # approx 30% tax bracket
        instruments.append({
            "section": "80C",
            "instrument": "ELSS Mutual Funds",
            "suggested_amount": amount,
            "estimated_tax_save": save,
            "risk": "moderate",
            "lock_in": "3 years",
            "score": score,
            "explanation": f"Remaining 80C limit: ₹{remaining_80c:,}. ELSS offers equity growth potential with tax benefit."
        })

    # NPS extra deduction
    if remaining_nps_extra > 0:
        score = 80 if risk_appetite != "low" else 65
        amount = remaining_nps_extra
        save = round(amount * 0.3)
        instruments.append({
            "section": "80CCD(1B)",
            "instrument": "NPS Tier-I",
            "suggested_amount": amount,
            "estimated_tax_save": save,
            "risk": "low-moderate",
            "lock_in": "till 60",
            "score": score,
            "explanation": "Extra ₹50,000 deduction beyond 80C — excellent for retirement planning."
        })

    # Health Insurance (80D)
    if remaining_80d > 0:
        score = 95
        amount = remaining_80d
        save = round(amount * 0.3)
        instruments.append({
            "section": "80D",
            "instrument": "Health Insurance Premium",
            "suggested_amount": amount,
            "estimated_tax_save": save,
            "risk": "none",
            "lock_in": "none",
            "score": score,
            "explanation": "Protect your family while getting deduction up to ₹25k/₹50k."
        })

    # Sort by score (highest first)
    instruments.sort(key=lambda x: x["score"], reverse=True)

    return {
        "recommended_regime": recommended_regime,
        "tax_new": tax_new,
        "tax_old": tax_old,
        "potential_savings": savings_if_new,
        "confidence": confidence,
        "recommendations": instruments[:3],  # top 3 only
        "disclaimer": "This is an estimate based on current rules (Jan 2026). Consult a qualified CA before investing or filing returns."
    }


# ── Quick test ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    sample_user = {
        "gross_income": 1500000,
        "age": 32,
        "current_80c": 50000,
        "current_80d": 15000,
        "risk_appetite": "medium"
    }

    result = generate_recommendations(sample_user)
    import json
    print(json.dumps(result, indent=2))