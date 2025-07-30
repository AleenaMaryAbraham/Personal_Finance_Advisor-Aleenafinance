import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Page settings
st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("💸 Personal Finance Advisor")
st.markdown("Upload your income and expense data to get savings/investment recommendations based on your financial profile.")

# Upload file
uploaded_file = st.file_uploader("Upload a CSV or Excel file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        # Load data
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("📊 Uploaded Data")
        st.dataframe(df)

        # Identify column names
        expense_cols = ['Expenses', 'Expense', 'Total Expense', 'Total Expenses']
        expense_col_found = next((col for col in expense_cols if col in df.columns), None)

        if 'Year' in df.columns and 'Income' in df.columns and expense_col_found:
            df = df.rename(columns={expense_col_found: 'Expenses'})
            df['Surplus'] = df['Income'] - df['Expenses']

            # Show summary metrics
            st.subheader("📈 Summary Metrics")
            avg_income = df['Income'].mean()
            avg_expenses = df['Expenses'].mean()
            avg_surplus = df['Surplus'].mean()
            st.metric("Avg Annual Income", f"₹{avg_income:,.2f}")
            st.metric("Avg Annual Expenses", f"₹{avg_expenses:,.2f}")
            st.metric("Avg Annual Surplus", f"₹{avg_surplus:,.2f}")

            # Visualization
            st.subheader("📉 Income vs Expenses Over Time")
            fig1 = px.line(df, x='Year', y=['Income', 'Expenses', 'Surplus'], markers=True)
            st.plotly_chart(fig1)

            st.subheader("💰 Surplus Distribution")
            fig2 = px.pie(df, values='Surplus', names='Year')
            st.plotly_chart(fig2)

            # Risk input
            st.subheader("⚖️ Choose Your Risk Appetite")
            risk = st.selectbox("Select your risk level", ["Low", "Medium", "High"])

            # Recommendations
            st.subheader("🧠 Investment Recommendation")
            if risk == "Low":
                recommendation = "Fixed Deposits, PPF, and low-risk instruments"
            elif risk == "Medium":
                recommendation = "Balanced Mutual Funds and SIPs"
            else:
                recommendation = "Equity Mutual Funds and Stocks"

            st.success(f"Recommended: {recommendation}")

            # SIP Calculator
            st.subheader("📅 SIP Calculator")
            sip_amt = st.number_input("Monthly Investment (₹)", min_value=0, value=5000)
            sip_years = st.slider("Investment Duration (years)", 1, 30, 5)
            sip_rate = st.slider("Expected Return Rate (%)", 1, 20, 12)

            months = sip_years * 12
            monthly_rate = sip_rate / 12 / 100
            sip_value = sip_amt * (((1 + monthly_rate) ** months - 1) * (1 + monthly_rate)) / monthly_rate
            st.success(f"SIP Value after {sip_years} years: ₹{sip_value:,.2f}")

            # FD Calculator
            st.subheader("🏦 Fixed Deposit Calculator")
            fd_amt = st.number_input("FD Amount (₹)", min_value=0, value=50000)
            fd_years = st.slider("FD Tenure", 1, 10, 3)
            fd_rate = st.slider("FD Interest Rate (%)", 1, 10, 6)

            fd_final = fd_amt * ((1 + fd_rate / 100) ** fd_years)
            st.success(f"FD Value after {fd_years} years: ₹{fd_final:,.2f}")

            # Final output
            st.subheader("📝 Final Advice")
            st.markdown(f"""
            Based on your **average annual surplus of ₹{avg_surplus:,.2f}** and your **{risk}** risk appetite, we recommend:

            - **{recommendation}**

            Keep tracking your finances and investing consistently. Your financial wellness is a journey—you're on the right path! 🌱
            """)

        else:
            st.error("Please ensure your data includes 'Year', 'Income', and an Expense column (like 'Expenses' or 'Total Expense').")

    except Exception as e:
        st.error(f"Something went wrong: {e}")
