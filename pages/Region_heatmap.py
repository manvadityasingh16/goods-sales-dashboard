import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("🗺️ Region-wise Sales Heatmap")

# Load data


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

# Bar Chart
st.subheader("🔥 Sales by Region")

region_sales = filtered_df.groupby("Region")["TotalSale"].sum().reset_index().sort_values(by="TotalSale", ascending=False)

fig, ax = plt.subplots()
sns.barplot(data=region_sales, x='Region', y='TotalSale', palette='coolwarm', ax=ax)
ax.set_ylabel("Total Sales (₹)")
ax.set_title("Total Sales per Region")
st.pyplot(fig)

# Optional: Show top region
if not region_sales.empty:
    top_region = region_sales.iloc[0]
    st.success(f"🏆 Top Region: {top_region['Region']} — ₹{int(top_region['TotalSale']):,}")
