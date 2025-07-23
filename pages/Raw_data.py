import streamlit as st
import pandas as pd
import io

st.title("📄 Raw Sales Data")

# Load data
df = pd.read_csv("goods_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Profit'] = df['TotalSale'] * 0.20

# Sidebar filters
st.sidebar.header("🧾 Filters for Raw Data")
regions = st.sidebar.multiselect("Region", df["Region"].unique(), default=list(df["Region"].unique()))
categories = st.sidebar.multiselect("Category", df["Category"].unique(), default=list(df["Category"].unique()))
date_range = st.sidebar.date_input("Date Range", [df['Date'].min(), df['Date'].max()])

# Apply filters
filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

st.subheader("🔍 Filtered Data Table")
st.write(f"Showing **{len(filtered_df)}** rows")
st.dataframe(filtered_df)

# --- Download CSV ---
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name='filtered_sales.csv',
    mime='text/csv'
)

# --- Download Excel ---
try:
    import xlsxwriter
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='SalesData')
        writer.close()
        st.download_button(
            label="📥 Download Excel",
            data=buffer,
            file_name='filtered_sales.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
except ImportError:
    st.warning("⚠️ Excel download not available. Run `pip install xlsxwriter` to enable.")
