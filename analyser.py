import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from fpdf import FPDF
import base64
from io import BytesIO

# Streamlit setup
st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("💸 Personal Finance Advisor")
st.markdown("""
This app recommends savings or investment plans based on your income, expenses, and risk appetite. 
Upload your historical income and expense data to get personalized suggestions and visual insights.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your income and expense data (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

def generate_pdf(data, avg_income, avg_expenses, avg_surplus, future_value, fd_return, risk, recommendation):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Personal Finance Analysis Report", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    # Summary
    pdf.cell(0, 10, f"Average Annual Income: ₹{avg_income:,.2f}", ln=True)
    pdf.cell(0, 10, f"Average Annual Expenses: ₹{avg_expenses:,.2f}", ln=True)
    pdf.cell(0, 10, f"Average Annual Surplus: ₹{avg_surplus:,.2f}", ln=True)
    pdf.ln(5)

    # Risk & Recommendations
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, f"Risk Appetite: {risk}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Recommended Strategy: {recommendation}")
    pdf.ln(3)

    # Calculators
    pdf.cell(0, 10, f"Estimated SIP Returns: ₹{future_value:,.2f}", ln=True)
    pdf.cell(0, 10, f"Estimated FD Returns: ₹{fd_return:,.2f}", ln=True)
    pdf.ln(5)

    # Advice
    summary = (
        f"Based on your financial data, your average surplus indicates you have consistent savings potential. "
        f"With a '{risk}' risk appetite, you should balance stability and growth. Your returns through SIP and FD "
        f"show good financial planning. Stay disciplined, review investments yearly, and aim for long-term goals."
    )
    pdf.set_font("Arial", 'I', 11)
    pdf.multi_cell(0, 10, f"\nAdvice: {summary}")
    
    # Convert PDF to byte stream
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_data = pdf_buffer.getvalue()
    return pdf_data

if uploaded_file:
    # Read data
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.subheader("📊 Uploaded Data")
    st.dataframe(data)

    # Check columns
    expense_cols = ['Expenses', 'Expense', 'Total Expense', 'Total Expenses']
    expense_col_found = next((col for col in expense_cols if col in data.columns), None)

    if 'Year' in data.columns and 'Income' in data.columns and expense_col_found:
        data = data.rename(columns={expense_col_found: 'Expenses'})
        data['Surplus'] = data['Income'] - data['Expenses']

        st.subheader("📈 Summary Metrics")
        avg_income = data['Income'].mean()
        avg_expenses = data['Expenses'].mean()
        avg_surplus = data['Surplus'].mean()
        st.metric("Average Annual Income", f"₹{avg_income:,.2f}")
        st.metric("Average Annual Expenses", f"₹{avg_expenses:,.2f}")
        st.metric("Average Annual Surplus", f"₹{avg_surplus:,.2f}")

        # Visualizations
        st.subheader("📉 Income vs Expenses Over Time")
        fig1 = px.line(data, x='Year', y=['Income', 'Expenses', 'Surplus'], markers=True)
        st.plotly_chart(fig1)

        st.subheader("💰 Surplus Distribution")
        fig2 = px.pie(data, values='Surplus', names='Year', title='Surplus Distribution by Year')
        st.plotly_chart(fig2)

        # Risk Appetite
        st.subheader("⚖️ Choose Your Risk Appetite")
        risk = st.selectbox("Risk Tolerance", ["Low", "Medium", "High"])

        st.markdown("### 🧠 Recommended Strategy")
        if risk == "Low":
            recommendation = "Fixed Deposits, Recurring Deposits, Public Provident Fund (PPF)"
        elif risk == "Medium":
            recommendation = "Balanced Mutual Funds, SIPs"
        else:
            recommendation = "Equity Mutual Funds, Direct Stocks"
        st.info(f"Recommended: {recommendation}")

        # SIP Calculator
        st.subheader("📅 SIP Calculator")
        sip_amount = st.number_input("Monthly Investment (₹)", min_value=0, value=5000)
        sip_years = st.slider("Investment Period (Years)", 1, 30, 5)
        sip_rate = st.slider("Expected Annual Return (%)", 1, 20, 12)
        months = sip_years * 12
        monthly_rate = sip_rate / 12 / 100
        future_value = sip_amount * (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate)) / monthly_rate
        st.success(f"Estimated SIP Returns after {sip_years} years: ₹{future_value:,.2f}")

        # FD Calculator
        st.subheader("🏦 Fixed Deposit Calculator")
        fd_principal = st.number_input("FD Principal Amount (₹)", min_value=0, value=50000)
        fd_years = st.slider("FD Tenure (Years)", 1, 10, 3)
        fd_rate = st.slider("FD Interest Rate (%)", 1, 10, 6)
        fd_return = fd_principal * ((1 + fd_rate / 100) ** fd_years)
        st.success(f"Estimated FD Returns after {fd_years} years: ₹{fd_return:,.2f}")

        # PDF Download
        st.subheader("📥 Download Your Report")
        if st.button("📄 Generate and Download Personalized PDF Report"):
    pdf_buffer = generate_pdf(
        data,
        avg_income,
        avg_expenses,
        avg_surplus,
        future_value,
        fd_return,
        risk,
        recommendation
    )

    st.download_button(
        label="⬇️ Click to Download Report",
        data=pdf_buffer,
        file_name="Personal_Finance_Report.pdf",
        mime="application/pdf"
    )
