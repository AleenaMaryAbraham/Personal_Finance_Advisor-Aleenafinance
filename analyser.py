import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page settings
st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("💸 Personal Finance Advisor")
st.markdown("""
Upload your income and expense data over the years to get smart savings/investment suggestions based on your risk profile, 
plus visual insights and calculators for SIP & FD returns.
""")

# File upload
uploaded_file = st.file_uploader("📂 Upload CSV/XLS/XLSX file with columns: Year, Income, Expense(s)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.subheader("📊 Uploaded Data")
    st.dataframe(data)

    # Handle column name variations
    expense_col = None
    if 'Expenses' in data.columns:
        expense_col = 'Expenses'
    elif 'Expense' in data.columns:
        expense_col = 'Expense'

    # Check required columns
    if {'Year', 'Income'}.issubset(data.columns) and expense_col:
        data['Surplus'] = data['Income'] - data[expense_col]

        # Summary
        st.subheader("📈 Summary Metrics")
        avg_income = data['Income'].mean()
        avg_expenses = data[expense_col].mean()
        avg_surplus = data['Surplus'].mean()
        st.metric("Average Annual Income", f"₹{avg_income:,.2f}")
        st.metric("Average Annual Expenses", f"₹{avg_expenses:,.2f}")
        st.metric("Average Annual Surplus", f"₹{avg_surplus:,.2f}")

        # Visualizations
        st.subheader("📉 Income vs Expenses Over Time")
        fig1 = px.line(data, x='Year', y=['Income', expense_col, 'Surplus'], markers=True,
                       labels={expense_col: "Expenses"})
        st.plotly_chart(fig1)

        st.subheader("💰 Surplus Distribution")
        fig2 = px.pie(data, values='Surplus', names='Year', title='Surplus Distribution by Year')
        st.plotly_chart(fig2)

        # Risk profile
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
        fd_rate = st.slider("FD Annual Interest Rate (%)", 1, 10, 6)

        fd_maturity = fd_principal * ((1 + fd_rate / 100) ** fd_years)
        st.success(f"Maturity Amount after {fd_years} years: ₹{fd_maturity:,.2f}")

    else:
        st.warning("Please make sure your file has columns: Year, Income, and Expense or Expenses.")
