import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os

# Try importing Gemini (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="Goods Sales Dashboard", layout="wide")

# ==============================
# LOAD DATA
# ==============================
st.sidebar.header("📂 Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

@st.cache_data
def load_data(file):
    if file is not None:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
    else:
        df = pd.read_excel("sales_dataset.xlsx")  # fallback default
    # Ensure correct column names
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if "Quantity" in df.columns and "Price" in df.columns:
        df["TotalSale"] = df["Quantity"] * df["Price"]
    return df

df = load_data(uploaded_file)

# ==============================
# SIDEBAR FILTERS
# ==============================
st.sidebar.header("🔍 Filters")
search_term = st.sidebar.text_input("Search Product")
categories = st.sidebar.multiselect("Select Categories", options=df["Category"].unique())
regions = st.sidebar.multiselect("Select Regions", options=df["Region"].unique())

if "Date" in df.columns:
    date_range = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])
else:
    date_range = None

filtered_df = df.copy()

if search_term:
    filtered_df = filtered_df[filtered_df["Product"].str.contains(search_term, case=False, na=False)]

if categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(categories)]

if regions:
    filtered_df = filtered_df[filtered_df["Region"].isin(regions)]

if date_range and len(date_range) == 2:
    start_date, end_date = date_range
    filtered_df = filtered_df[(filtered_df["Date"] >= pd.to_datetime(start_date)) &
                              (filtered_df["Date"] <= pd.to_datetime(end_date))]

# ==============================
# MAIN DASHBOARD
# ==============================
st.title("📊 Goods Sales Dashboard")

# ===== KPIs =====
st.subheader("📌 Key Metrics")
if not filtered_df.empty:
    total_sales = filtered_df["TotalSale"].sum()
    total_orders = len(filtered_df)
    total_quantity = filtered_df["Quantity"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 Total Sales", f"₹{int(total_sales):,}")
    col2.metric("📦 Total Orders", f"{total_orders:,}")
    col3.metric("🛒 Total Quantity Sold", f"{total_quantity:,}")
else:
    st.warning("⚠️ No data available for current filters.")

# ===== Sales Over Time =====
st.subheader("📈 Sales Over Time")
if not filtered_df.empty and "Date" in filtered_df.columns:
    sales_over_time = filtered_df.groupby("Date")["TotalSale"].sum().reset_index()
    fig, ax = plt.subplots()
    sns.lineplot(x="Date", y="TotalSale", data=sales_over_time, ax=ax)
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales (INR)")
    ax.set_title("Daily Sales")
    st.pyplot(fig)
else:
    st.warning("⚠️ No data available to display sales over time.")

# ===== Sales by Category =====
st.subheader("🧺 Sales by Category")
if not filtered_df.empty:
    cat_sales = filtered_df.groupby("Category")["TotalSale"].sum().sort_values()
    st.bar_chart(cat_sales)
else:
    st.warning("⚠️ No category data available.")

# ===== Regional Sales Share =====
st.subheader("🌍 Regional Sales Share")
if not filtered_df.empty:
    region_sales = filtered_df.groupby("Region")["TotalSale"].sum().reset_index()
    fig = px.pie(
        region_sales,
        names="Region",
        values="TotalSale",
        hole=0.4,
        title="Share of Sales by Region",
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig.update_traces(textinfo="percent+label")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ No regional sales data available.")

# ===== Best Performing Month =====
st.subheader("📆 Best Performing Month")
if not filtered_df.empty and "Date" in filtered_df.columns:
    monthly_sales = filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["TotalSale"].sum().reset_index()
    monthly_sales["Date"] = monthly_sales["Date"].astype(str)
    if not monthly_sales.empty:
        best_month = monthly_sales.sort_values(by="TotalSale", ascending=False).iloc[0]
        st.success(f"🏅 Highest Sales Month: {best_month['Date']} — ₹{int(best_month['TotalSale']):,}")
        st.line_chart(monthly_sales.set_index("Date")["TotalSale"])
else:
    st.warning("⚠️ No monthly sales data available.")

# ===== Region-wise Sales Heatmap =====
st.subheader("🗺️ Region-wise Sales Heatmap")
if not filtered_df.empty:
    region_sales = filtered_df.groupby("Region")["TotalSale"].sum().reset_index()
    fig, ax = plt.subplots()
    sns.barplot(x="Region", y="TotalSale", data=region_sales, palette="coolwarm", ax=ax)
    st.pyplot(fig)
else:
    st.warning("⚠️ No region-wise data available.")

# ===== Raw Data =====
st.subheader("📋 Filtered Sales Data")
if not filtered_df.empty:
    st.dataframe(filtered_df)
else:
    st.info("ℹ️ No data matches your filters or search term.")

# ==============================
# GEMINI Q&A SECTION
# ==============================
st.sidebar.header("🤖 Gemini Assistant")

if GEMINI_AVAILABLE:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        st.sidebar.error("⚠️ GOOGLE_API_KEY not set. Please set it in environment variables.")
    else:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        st.subheader("💬 Ask Gemini About Your Data")
        user_question = st.text_area("Type your question:")

        if st.button("Ask Gemini"):
            if not filtered_df.empty:
                context = filtered_df.head(200).to_csv(index=False)  # sample context
                try:
                    response = model.generate_content([
                        f"You are a data assistant. Answer questions about this sales data:\n\n{context}",
                        user_question
                    ])
                    st.write("🤖 Gemini Answer:")
                    st.success(response.text)
                except Exception as e:
                    st.error(f"❌ Gemini error: {e}")
            else:
                st.warning("⚠️ No data to analyze.")
else:
    st.sidebar.warning("⚠️ Gemini SDK not installed. Run: pip install google-generativeai")
