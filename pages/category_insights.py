import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

st.title("📊 Category Insights")

# Load and prep data
df = pd.read_csv("goods_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Profit'] = df['TotalSale'] * 0.20

# Sidebar filters
st.sidebar.header("🔍 Filters for Category Insights")
regions = st.sidebar.multiselect("Region", df["Region"].unique(), default=list(df["Region"].unique()))
categories = st.sidebar.multiselect("Category", df["Category"].unique(), default=list(df["Category"].unique()))
date_range = st.sidebar.date_input("Date Range", [df['Date'].min(), df['Date'].max()])

# Filter
filtered_df = df[
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories)) &
    (df["Date"] >= pd.to_datetime(date_range[0])) &
    (df["Date"] <= pd.to_datetime(date_range[1]))
]

# Sales by category
st.subheader("🧺 Total Sales by Category")
cat_sales = filtered_df.groupby('Category')['TotalSale'].sum().sort_values(ascending=True)
st.bar_chart(cat_sales)

# Regional Sales Share (Donut chart)
st.subheader("🌍 Sales by Region (Donut Chart)")
region_sales = filtered_df.groupby("Region")["TotalSale"].sum().reset_index()

fig = px.pie(
    region_sales,
    names='Region',
    values='TotalSale',
    hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig.update_traces(textinfo='percent+label')
st.plotly_chart(fig)

# Category Profit Summary
st.subheader("📦 Profit by Category")
category_summary = (
    filtered_df.groupby("Category")
    .agg(Total_Sales=("TotalSale", "sum"), Total_Profit=("Profit", "sum"))
    .reset_index()
)
st.dataframe(category_summary.style.format({"Total_Sales": "₹{:,}", "Total_Profit": "₹{:,}"}))
