import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go

st.set_page_config(page_title="Personal Finance Advisor", layout="centered")

# Title
st.title("💸 Personal Finance Advisor")
st.write("Get personalized savings or investment advice based on your goals.")

# Sidebar Input
st.sidebar.header("Enter Your Financial Details")
income = st.sidebar.number_input("Monthly Income (₹)", min_value=0.0, step=100.0)
expenses = st.sidebar.number_input("Monthly Expenses (₹)", min_value=0.0, step=100.0)
risk = st.sidebar.radio("Your Risk Appetite", ["Low", "Moderate", "High"])

surplus = income - expenses

# Show a quick summary
st.subheader("📊 Financial Summary")
st.metric("Monthly Surplus (₹)", f"{surplus:,.2f}")
fig = go.Figure()
fig.add_trace(go.Pie(labels=["Expenses", "Surplus"], values=[expenses, surplus], hole=0.5))
st.plotly_chart(fig, use_container_width=True)

# Recommendation Logic
st.subheader("🤖 Investment Recommendation")
if surplus <= 0:
    st.warning("Your expenses exceed or equal income. Reduce expenses to start saving.")
else:
    if risk == "Low":
        rec = "Fixed Deposit (FD), Recurring Deposit (RD), Public Provident Fund (PPF)"
    elif risk == "Moderate":
        rec = "Systematic Investment Plan (SIP), Balanced Mutual Funds"
    else:
        rec = "Equity Mutual Funds, Stocks, SIP in ELSS"

    st.success(f"Based on your risk profile, consider investing in: **{rec}**")

# --- Calculators ---
st.header("📈 Investment Calculators")

with st.expander("💼 Fixed Deposit (FD) Calculator"):
    fd_amount = st.number_input("FD Amount (₹)", min_value=0.0, step=100.0)
    fd_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0, max_value=15.0, step=0.1)
    fd_years = st.number_input("Time Period (Years)", min_value=1, max_value=30, step=1)
    if st.button("Calculate FD Returns"):
        fd_maturity = fd_amount * (1 + fd_rate/100)**fd_years
        st.success(f"Maturity Amount after {fd_years} years: ₹{fd_maturity:,.2f}")

with st.expander("📅 SIP Calculator"):
    sip_amount = st.number_input("Monthly SIP Investment (₹)", min_value=0.0, step=100.0)
    sip_rate = st.number_input("Expected Annual Return (%)", min_value=0.0, max_value=20.0, step=0.5)
    sip_years = st.number_input("Investment Duration (Years)", min_value=1, max_value=30, step=1)
    if st.button("Calculate SIP Returns"):
        r = (sip_rate / 100) / 12
        n = sip_years * 12
        future_value = sip_amount * (((1 + r)**n - 1) * (1 + r)) / r
        st.success(f"Projected SIP Value: ₹{future_value:,.2f}")

        # SIP Growth Chart
        months = np.arange(1, n+1)
        values = [sip_amount * (((1 + r)**i - 1) * (1 + r)) / r for i in months]
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=months, y=values, mode='lines+markers', name='Projected Value'))
        fig2.update_layout(title="📈 SIP Growth Over Time", xaxis_title="Months", yaxis_title="Investment Value (₹)")
        st.plotly_chart(fig2, use_container_width=True)

# Footer
st.caption("Made with 💙 using Streamlit | For educational purposes only.")
