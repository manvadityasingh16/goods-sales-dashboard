import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("🧪 Exploratory Data Analysis (EDA)")

# Load and prepare data
df = pd.read_csv("goods_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Profit'] = df['TotalSale'] * 0.20

# Sidebar filters
st.sidebar.header("🔍 Filters for EDA")
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

# Top 10 products
st.subheader("🏆 Top 10 Products by Sales")
top_products = filtered_df.groupby('Product')['TotalSale'].sum().sort_values(ascending=False).head(10)

fig, ax = plt.subplots()
sns.barplot(y=top_products.index, x=top_products.values, palette="viridis", ax=ax)
ax.set_xlabel("Total Sales (₹)")
ax.set_ylabel("Product")
st.pyplot(fig)

# Daily Sales Distribution - Boxplot
st.subheader("📉 Daily Sales Distribution")
daily_sales = filtered_df.groupby("Date")["TotalSale"].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 4))
sns.boxplot(data=daily_sales, y="TotalSale", color='coral', ax=ax)
ax.set_ylabel("Daily Sales (₹)")
st.pyplot(fig)

# Category Summary Table
st.subheader("📦 Category Performance Summary")
summary = (
    filtered_df.groupby("Category")
    .agg(Total_Sales=("TotalSale", "sum"), Avg_Profit=("Profit", "mean"))
    .reset_index()
)
st.dataframe(summary.style.format({"Total_Sales": "₹{:,}", "Avg_Profit": "₹{:.2f}"}))
