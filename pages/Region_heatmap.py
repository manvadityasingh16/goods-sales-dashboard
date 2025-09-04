import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from google import genai  # Gemini SDK

# =========================
# Load Data
# =========================
st.title("🗺️ Region-wise Sales Heatmap")

df = pd.read_csv("goods_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'])

# Sidebar filters
st.sidebar.header("🌍 Filters for Region View")
regions = st.sidebar.multiselect("Region", df["Region"].unique(), default=list(df["Region"].unique()))
categories = st.sidebar.multiselect("Category", df["Category"].unique(), default=list(df["Category"].unique()))
date_range = st.sidebar.date_input("Date Range", [df['Date'].min(), df['Date'].max()])

# Filter data
filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# =========================
# Bar Chart
# =========================
st.subheader("🔥 Sales by Region")

region_sales = filtered_df.groupby("Region")["TotalSale"].sum().reset_index().sort_values(by="TotalSale", ascending=False)

fig, ax = plt.subplots()
sns.barplot(data=region_sales, x='Region', y='TotalSale', palette='coolwarm', ax=ax)
ax.set_ylabel("Total Sales (₹)")
ax.set_title("Total Sales per Region")
st.pyplot(fig)

if not region_sales.empty:
    top_region = region_sales.iloc[0]
    st.success(f"🏆 Top Region: {top_region['Region']} — ₹{int(top_region['TotalSale']):,}")

# =========================
# Q&A Section
# =========================
st.subheader("🤖 Ask Questions About the Data")

question = st.text_input("Type your question here...")

if question:
    answer = None

    # ---- Structured Pandas answers ----
    if "highest selling product" in question.lower():
        top_product = (
            filtered_df.groupby("Product")["TotalSale"].sum().reset_index()
            .sort_values(by="TotalSale", ascending=False)
        )
        if not top_product.empty:
            answer = f"🏆 Highest selling product is **{top_product.iloc[0]['Product']}** with total sales of ₹{int(top_product.iloc[0]['TotalSale']):,}"

    elif "highest sale price" in question.lower():
        max_price = filtered_df.loc[filtered_df["Price"].idxmax()]
        answer = f"💰 Product with highest price is **{max_price['Product']}** at ₹{int(max_price['Price']):,}"

    elif "top customer" in question.lower():
        top_customer = (
            filtered_df.groupby("CustomerName")["TotalSale"].sum().reset_index()
            .sort_values(by="TotalSale", ascending=False)
        )
        if not top_customer.empty:
            answer = f"👤 Top customer is **{top_customer.iloc[0]['CustomerName']}** with total purchases worth ₹{int(top_customer.iloc[0]['TotalSale']):,}"

    elif "region" in question.lower():
        if not region_sales.empty:
            answer = f"🌍 The top region is **{top_region['Region']}** with ₹{int(top_region['TotalSale']):,} in sales."

    # ---- If pandas has no answer, fallback to Gemini ----
    if not answer:
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            response = client.models.generate_content(
                model="gemini-1.5-pro",
                contents=f"The user asked: {question}\nHere is the data: {filtered_df.head(20).to_string()}"
            )
            answer = response.text
        except Exception as e:
            answer = f"⚠️ Gemini error: {e}"

    st.info(answer)
