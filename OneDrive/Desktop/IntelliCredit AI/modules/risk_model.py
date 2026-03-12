def calculate_risk_score(data):
    """
    Simulates ML model risk scoring.
    Score is 0-100 (100 is best, 0 is default/worst).
    Returns (score, category, shap_factors)
    """
    base_score = 100
    
    debt_ratio = data['debt'] / data['revenue'] if data['revenue'] > 0 else 1
    
    # Simple logic
    debt_penalty = min(30, int(debt_ratio * 40))
    litigation_penalty = int(data['litigations'] * 15)
    growth_bonus = min(15, int(data['revenue_growth'] * 1.5))
    sentiment_bonus = int(data['sentiment'] * 10)
    
    final_score = base_score - debt_penalty - litigation_penalty + growth_bonus + sentiment_bonus
    final_score = max(0, min(100, final_score))
    
    if final_score >= 75:
        category = "Low Risk"
    elif final_score >= 50:
        category = "Medium Risk"
    else:
        category = "High Risk"
        
    shap_factors = [
        {"feature": "Revenue Growth", "impact": f"+{growth_bonus} risk score", "type": "positive"},
        {"feature": "Debt Ratio", "impact": f"-{debt_penalty} risk score", "type": "negative"},
        {"feature": "Legal/Litigations", "impact": f"-{litigation_penalty} risk score", "type": "negative" if litigation_penalty > 0 else "neutral"}
    ]
    
    # Ensure they are sorted by absolute impact
    # but we just return them for the UI mock
    
    return final_score, category, shap_factors

def get_loan_decision(score, data):
    """
    Returns (decision, amount, rate, reasons) based on score.
    """
    if score >= 75:
        decision = "APPROVE"
        amount = "$5,000,000"
        rate = "7.5%"
        reasons = [
            "Strong revenue growth momentum",
            "Optimal debt capitalization structure",
            "High net positive sentiment & zero legal risks"
        ]
    elif score >= 50:
        decision = "MANUAL REVIEW REQUIRED"
        amount = "$1,500,000"
        rate = "10.2%"
        reasons = [
            "Moderate sector risk identified",
            "Debt-to-revenue ratio requires monitoring",
            "Adequate interest coverage ratio"
        ]
    else:
        decision = "REJECT"
        amount = "$0"
        rate = "N/A"
        reasons = [
            "Elevated litigation risk detected",
            "High debt leveraging",
            "Unfavorable sentiment indicators"
        ]
        
    return decision, amount, rate, reasons
