import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Title and description
st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("💸 Personal Finance Advisor")
st.markdown("""
This app recommends savings or investment plans based on your income, expenses, and risk appetite. 
Upload your historical income and expense data to get personalized suggestions and visual insights.
""")

# Upload file
uploaded_file = st.file_uploader("Upload your income and expense data (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    # Read data
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.subheader("📊 Uploaded Data")
    st.dataframe(data)

    # Check for required columns
    expense_cols = ['Expenses', 'Expense', 'Total Expense', 'Total Expenses']
    expense_col_found = None
    for col in expense_cols:
        if col in data.columns:
            expense_col_found = col
            break

    if 'Year' in data.columns and 'Income' in data.columns and expense_col_found:
        # Rename expense column to a consistent name
        data = data.rename(columns={expense_col_found: 'Expenses'})

        # Calculate surplus
        data['Surplus'] = data['Income'] - data['Expenses']

        # Summary Metrics
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
            st.info("Recommended: Fixed Deposits, Recurring Deposits, Public Provident Fund (PPF)")
        elif risk == "Medium":
            st.info("Recommended: Balanced Mutual Funds, SIPs")
        else:
            st.info("Recommended: Equity Mutual Funds, Direct Stocks")

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

    else:
        st.error("Please make sure your file has columns: 'Year', 'Income', and one of: 'Expense', 'Expenses', 'Total Expense', or 'Total Expenses'.")

import base64
from io import BytesIO
from fpdf import FPDF

# Final Recommendation Summary
st.subheader("📌 Final Summary & Suggestions")
recommendation = ""
if risk == "Low":
    recommendation = "Your risk profile is Low. Consider safe investments like Fixed Deposits, PPF, and RDs to preserve capital."
elif risk == "Medium":
    recommendation = "Your risk profile is Medium. SIPs and Balanced Mutual Funds could offer a mix of growth and safety."
else:
    recommendation = "Your risk profile is High. You may explore Equity Mutual Funds and Direct Stock investments for higher returns."

st.markdown(f"""
**🧾 Summary Advice:**
- Based on your average annual surplus of ₹{avg_surplus:,.2f}, a monthly SIP of ₹{sip_amount} for {sip_years} years can grow to ₹{future_value:,.2f}.
- Alternatively, a fixed deposit of ₹{fd_principal} for {fd_years} years at {fd_rate}% interest may yield ₹{fd_return:,.2f}.
- {recommendation}
""")

# Generate PDF Report
def generate_pdf(data, avg_income, avg_expenses, avg_surplus, future_value, fd_return, risk, recommendation):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Personal Finance Report", ln=True, align="C")
    pdf.ln(10)

    pdf.cell(200, 10, txt="📊 Summary Statistics:", ln=True)
    pdf.cell(200, 10, txt=f"Average Annual Income: ₹{avg_income:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Average Annual Expenses: ₹{avg_expenses:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Average Annual Surplus: ₹{avg_surplus:,.2f}", ln=True)
    pdf.ln(5)

    pdf.cell(200, 10, txt="💰 Investment Results:", ln=True)
    pdf.cell(200, 10, txt=f"SIP Future Value: ₹{future_value:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"FD Returns: ₹{fd_return:,.2f}", ln=True)
    pdf.ln(5)

    pdf.cell(200, 10, txt="🧠 Risk Profile and Suggestions:", ln=True)
    pdf.multi_cell(0, 10, txt=recommendation)

    buffer = BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

# Download button
st.subheader("📥 Download Your Report")
if st.button("Generate PDF Report"):
    pdf_data = generate_pdf(
        data, avg_income, avg_expenses, avg_surplus,
        future_value, fd_return, risk, recommendation
    )
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="Personal_Finance_Report.pdf">📄 Click here to download your report</a>'
    st.markdown(href, unsafe_allow_html=True)
