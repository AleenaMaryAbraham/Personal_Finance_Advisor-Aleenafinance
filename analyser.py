import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
from fpdf import FPDF

st.set_page_config(page_title="Personal Finance Advisor", layout="centered")
st.title("📊 Personal Finance Advisor")
st.markdown("""
Upload your income and expense data to receive personalized financial advice. 

**File Requirements:**
- Accepted formats: `.csv`, `.xls`, `.xlsx`
- Required columns: `Date` or `Year`, `Salary` or `Income`, and either:
  - `Expense`, `Expenses`, `Total Expense`, or `Total Expenses`
  
OR: granular expense categories like `Rent`, `Groceries`, `Entertainment`, etc. (we'll sum them).
""")

# Upload file
uploaded_file = st.file_uploader("Upload your file", type=["csv", "xls", "xlsx"])

# --- Helper Functions ---
def convert_df_to_pdf(df, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary)

    pdf.ln()
    pdf.set_font("Arial", size=10)
    for col in df.columns:
        pdf.cell(40, 10, col, 1)
    pdf.ln()

    for _, row in df.iterrows():
        for item in row:
            pdf.cell(40, 10, str(item), 1)
        pdf.ln()

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

# --- Main Logic ---
if uploaded_file:
    try:
        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.subheader("Preview of Uploaded Data")
        st.dataframe(df.head())

        # Standardize column names
        df.columns = df.columns.str.strip().str.lower()
        col_map = {
            'salary': 'income',
            'total income': 'income',
            'year': 'year',
            'date': 'year',
            'expenses': 'expense',
            'total expenses': 'expense',
            'total expense': 'expense',
        }
        df.rename(columns=col_map, inplace=True)

        # Infer income and expenses
        income_col = next((col for col in df.columns if 'income' in col), None)
        year_col = next((col for col in df.columns if 'year' in col), None)

        # Handle granular expenses if needed
        if 'expense' not in df.columns:
            expense_cols = [col for col in df.columns if col not in [income_col, year_col] and df[col].dtype != 'O']
            df['expense'] = df[expense_cols].sum(axis=1)

        # Final check
        if not all([income_col, year_col, 'expense' in df.columns]):
            st.error("Please make sure your file has columns: 'Year', 'Income', and either 'Expense' or granular expense categories.")
        else:
            df = df[[year_col, income_col, 'expense']].copy()
            df.rename(columns={year_col: 'Year', income_col: 'Income', 'expense': 'Expenses'}, inplace=True)
            df['Savings'] = df['Income'] - df['Expenses']
            df['Savings Rate (%)'] = (df['Savings'] / df['Income']) * 100

            st.success("✅ Financial summary computed!")
            st.subheader("📈 Summary Table")
            st.dataframe(df)

            # --- Visualizations ---
            st.subheader("📊 Visualizations")
            fig, ax = plt.subplots(figsize=(10, 5))
            df.plot(x='Year', y=['Income', 'Expenses', 'Savings'], kind='bar', ax=ax)
            plt.title("Yearly Income, Expenses, and Savings")
            plt.ylabel("Amount")
            st.pyplot(fig)

            # --- Advice Paragraph ---
            avg_saving_rate = df['Savings Rate (%)'].mean()
            if avg_saving_rate > 30:
                advice = "You're saving quite well! Consider diversifying your investments in SIPs or mutual funds."
            elif avg_saving_rate > 15:
                advice = "Good job maintaining savings. You may explore safer investments like Fixed Deposits or a balanced SIP."
            else:
                advice = "Your savings rate is low. Focus on reducing discretionary spending and build an emergency fund first."

            summary_text = f"Based on your data, your average annual savings rate is approximately {avg_saving_rate:.2f}%. {advice}"

            st.subheader("📝 Personalized Advice")
            st.markdown(f"""
            **Advice Summary**
            > {summary_text}
            """)

            # --- Download PDF ---
            pdf_data = convert_df_to_pdf(df, summary_text)
            st.download_button(
                label="📄 Download PDF Report",
                data=pdf_data,
                file_name="personal_finance_report.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"Something went wrong: {e}")
