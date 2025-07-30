import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from fpdf import FPDF

st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("💸 Personal Finance Advisor – AleenaFinance")

st.markdown("""
Upload your monthly income and expense data (in CSV/XLS/XLSX format). The app will compute:
- Yearly average income and expenses
- Annual surplus or deficit
- A forecast for next year's savings
- Risk analysis
- And a downloadable PDF report with recommendations
""")

# Function to generate PDF report
def generate_pdf(data, avg_income, avg_expenses, avg_surplus, future_value, fd_return, risk, recommendation):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Personal Finance Report", ln=True, align='C')
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"Average Annual Income: ₹{avg_income:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Average Annual Expenses: ₹{avg_expenses:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Average Annual Surplus: ₹{avg_surplus:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Estimated Next Year Surplus: ₹{future_value:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Expected FD Return (6%): ₹{fd_return:,.2f}", ln=True)
    pdf.cell(200, 10, txt=f"Risk Assessment: {risk}", ln=True)

    pdf.ln(10)
    pdf.multi_cell(0, 10, txt="Recommendation: " + recommendation)

    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    return pdf_output.getvalue()

# File uploader
uploaded_file = st.file_uploader("Upload your income-expense data file", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Normalize column names
        df.columns = [col.strip().capitalize() for col in df.columns]

        # Map expense-related column
        expense_col_candidates = ['Expense', 'Expenses', 'Total expense', 'Total expenses']
        expense_col = next((col for col in df.columns if col.lower() in [e.lower() for e in expense_col_candidates]), None)

        if 'Year' in df.columns and 'Income' in df.columns and expense_col:
            df = df[['Year', 'Income', expense_col]]
            df.rename(columns={expense_col: 'Expenses'}, inplace=True)

            df['Surplus'] = df['Income'] - df['Expenses']

            avg_income = df['Income'].mean()
            avg_expenses = df['Expenses'].mean()
            avg_surplus = df['Surplus'].mean()

            future_value = avg_surplus * 1.1
            fd_return = future_value * 1.06

            risk = "Low" if avg_expenses < avg_income else "High"
            recommendation = (
                "Your spending habits are healthy. Maintain a budget to keep expenses under control and consider investing surplus in low-risk instruments like Fixed Deposits or SIPs."
                if risk == "Low" else
                "You are overspending. Try to categorize your expenses and reduce discretionary spending. A budget tracker can help."
            )

            # Visualizations
            st.subheader("📊 Visualizations")
            fig, ax = plt.subplots()
            sns.lineplot(data=df, x='Year', y='Income', label='Income')
            sns.lineplot(data=df, x='Year', y='Expenses', label='Expenses')
            sns.lineplot(data=df, x='Year', y='Surplus', label='Surplus')
            plt.legend()
            st.pyplot(fig)

            # Display key metrics
            st.subheader("📌 Summary")
            st.write(f"**Average Income:** ₹{avg_income:,.2f}")
            st.write(f"**Average Expenses:** ₹{avg_expenses:,.2f}")
            st.write(f"**Average Surplus:** ₹{avg_surplus:,.2f}")
            st.write(f"**Next Year Surplus Projection:** ₹{future_value:,.2f}")
            st.write(f"**FD Return (6%):** ₹{fd_return:,.2f}")
            st.write(f"**Risk Profile:** {risk}")
            st.markdown(f"**💡 Advice:** {recommendation}")

            # PDF download
            st.subheader("📥 Download Your Report")
            if st.button("📄 Generate and Download Personalized PDF Report"):
                pdf_buffer = generate_pdf(
                    df, avg_income, avg_expenses, avg_surplus, future_value, fd_return, risk, recommendation
                )
                st.download_button(
                    label="⬇️ Click to Download Report",
                    data=pdf_buffer,
                    file_name="Personal_Finance_Report.pdf",
                    mime="application/pdf"
                )
        else:
            st.error("Please make sure your file has columns: 'Year', 'Income', and one of: 'Expense', 'Expenses', 'Total Expense', or 'Total Expenses'.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
