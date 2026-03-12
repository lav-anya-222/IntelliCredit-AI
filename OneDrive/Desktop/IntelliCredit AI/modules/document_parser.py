import time
import random

def extract_financial_data(files):
    """
    Simulates text extraction from PDFs using PDFPlumber/OCR.
    Returns structured financial data based on mock processing.
    """
    # Simulate processing time
    time.sleep(2)
    
    # Mock extracted financial data
    # Randomize slightly for variation across runs
    rev_base = 12000000
    rev_growth = random.uniform(8.0, 15.5)
    debt = rev_base * random.uniform(0.15, 0.4)
    ebitda = rev_base * 0.25
    assets = rev_base * 1.5
    liabilities = debt * 1.2
    
    data = {
        "revenue": round(rev_base, 2),
        "revenue_growth": round(rev_growth, 2),
        "debt": round(debt, 2),
        "ebitda": round(ebitda, 2),
        "icr": round(ebitda / (debt * 0.08) if debt > 0 else 10, 2), # Mock interest at 8%
        "litigations": 0 if random.random() > 0.2 else random.randint(1, 2),
        "sentiment": random.uniform(0.6, 0.95), # Mock positive sentiment from News/Legal NLP
        "total_assets": round(assets, 2),
        "total_liabilities": round(liabilities, 2),
        "net_worth": round(assets - liabilities, 2),
        "sector_risk": random.choice(["Low", "Medium"])
    }
    return data
