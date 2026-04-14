# IntelliCredit AI 🏦
**Automated Corporate Credit Intelligence Platform**

This is a prototype web application for the National AI/ML Hackathon by Vivriti Capital at Yuvaan IIT Hyderabad. It demonstrates an AI-powered system that automates corporate credit assessment from financial documents and generates a Credit Appraisal Memo (CAM).

## Features
1. **Document Upload**: Interface for uploading GST reports, Bank statements, and Financial statements.
2. **AI Financial Dashboard**: Displays extracted financial insights, including revenue, debt, and litigations with a trend chart.
3. **Credit Risk Engine**: Mock machine learning risk engine that calculates a 0-100 risk score based on uploaded data and presents an Explainable AI summary.
4. **CAM Report Generator**: Automatically generates a highly detailed Credit Appraisal Memo combining the metrics and the AI's final decision.

## Instructions to Run Locally
1. Ensure you have Python installed (Python 3.8+ recommended).
2. Install the required libraries via pip:
   ```bash
   pip install streamlit pandas numpy matplotlib pdfplumber spacy textblob
   ```
3. Run the application using Streamlit:
   ```bash
   streamlit run app.py
   ```
4. The dashboard will automatically open in your default web browser (typically at `http://localhost:8501`).

---

## Prototype Screenshots Description (For PPT)

To present this prototype effectively in your pitch deck, you can take the following screenshots once the app is running:

1. **Slide 1: Problem & Solution (The Upload Interface)**
   - **Screenshot Description**: The main "Upload Documents" tab showing the three upload zones (GST, Bank, Financials). This highlights the streamlined, intuitive starting point for the automated process.

2. **Slide 2: Data Extraction & Real-time Insights (AI Financial Dashboard)**
   - **Screenshot Description**: Navigate to the "AI Financial Dashboard" tab after clicking "Analyze with AI". Take a screenshot of the top metric cards (Revenue, Debt/EBITDA, Legal Cases) along with the "Financial Trends Overview" line chart. This visualizes the immediate value-add of automated document processing.

3. **Slide 3: Evaluating Risk & Explainable AI (Credit Risk Engine)**
   - **Screenshot Description**: A screenshot of the "Credit Risk Engine" tab. Make sure the large color-coded "Overall Risk Score" and the "Explainable AI (SHAP Features)" sections are clearly visible. This demonstrates transparency in the AI's decision-making block.

4. **Slide 4: Automated Output (CAM Report Generator)**
   - **Screenshot Description**: A snippet of the "Credit Appraisal Memo" tab, showcasing the clear "AI Engine Decision" (Approved/Rejected) and the neatly formatted, AI-generated text memo block. This proves the end-to-end automation capability, saving underwriters hours of manual work.
