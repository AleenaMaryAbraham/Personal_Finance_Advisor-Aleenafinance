import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Title
st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("💸 Personal Finance Advisor")
st.markdown("""
This app recommends savings or investment plans based on your income, expenses, and risk appetite. 
Upload your historical income and expense data to get personalized suggestions and visual insights.
""")

# Upload data file
uploaded_file = st.file_uploader("Upload your income and expense data (CSV, XLS, XLSX)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    st.subheader("📊 Uploaded Data")
    st.dataframe(data)

    # Ensure the correct columns exist
    if {'Year', 'Income', 'Expenses'}.issubset(data.columns):
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

        # Risk appetite selection
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
        fd_rate = st.s
