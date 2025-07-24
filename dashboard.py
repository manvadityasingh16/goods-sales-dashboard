import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io

# 🎨 Set Dark Mode styling
bg_color = "#0e1117"
font_color = "#FAFAFA"
plot_color = "whitegrid"

# Inject Custom CSS
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {font_color};
    }}
    .element-container:has(div[data-testid="metric-container"]) span {{
        color: {font_color} !important;
    }}
    .element-container:has(div[data-testid="metric-container"]) > div {{
        color: {font_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Seaborn dark styling
sns.set_style(plot_color)

# 📦 Load dataset
df = pd.read_csv("goods_sales_data.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Profit'] = df['TotalSale'] * 0.20  # add profit column

# 🧭 Page title
st.title("🛒 Goods & Sales Dashboard")
st.markdown("### 📊 Explore sales trends, regions, and products")

# 🔍 Sidebar Filters
st.sidebar.header("Filter Data")
region = st.sidebar.multiselect("Select Region", df["Region"].unique(), default=df["Region"].unique())
category = st.sidebar.multiselect("Select Category", df["Category"].unique(), default=df["Category"].unique())
date_range = st.sidebar.date_input("Select Date Range", [df['Date'].min(), df['Date'].max()])

# 🧹 Apply Filters
filtered_df = df[
    (df['Region'].isin(region)) &
    (df['Category'].isin(category)) &
    (df['Date'] >= pd.to_datetime(date_range[0])) &
    (df['Date'] <= pd.to_datetime(date_range[1]))
]

# 📊 Metrics
col1, col2, col3 = st.columns(3)
total_sales = filtered_df['TotalSale'].sum()
total_profit = filtered_df['Profit'].sum()
col1.metric("💰 Total Sales", f"₹{int(total_sales):,}")
col2.metric("📈 Profit", f"₹{int(total_profit):,}")
col3.metric("🧾 Orders", f"{len(filtered_df)}")

# ⏳ Sales Over Time
st.subheader("📈 Sales Over Time")
sales_over_time = filtered_df.groupby('Date')['TotalSale'].sum().reset_index()
fig, ax = plt.subplots()
sns.lineplot(x='Date', y='TotalSale', data=sales_over_time, ax=ax)
ax.set_xlabel("Date")
ax.set_ylabel("Sales (INR)")
ax.set_title("Daily Sales")
st.pyplot(fig)

# 🧺 Sales by Category
st.subheader("🧺 Sales by Category")
cat_sales = filtered_df.groupby('Category')['TotalSale'].sum().sort_values()
st.bar_chart(cat_sales)

# 🌍 Regional Sales Share
st.subheader("🌍 Regional Sales Share")
region_sales = filtered_df.groupby("Region")["TotalSale"].sum().reset_index()
fig = px.pie(
    region_sales,
    names='Region',
    values='TotalSale',
    hole=0.4,
    title="Share of Sales by Region",
    color_discrete_sequence=px.colors.sequential.RdBu
)
fig.update_traces(textinfo='percent+label')
st.plotly_chart(fig, use_container_width=True)

# 🏆 Best Performing Month
st.subheader("📆 Best Performing Month")
monthly_sales = filtered_df.groupby(filtered_df['Date'].dt.to_period("M"))['TotalSale'].sum().reset_index()
monthly_sales['Date'] = monthly_sales['Date'].astype(str)
best_month = monthly_sales.sort_values(by='TotalSale', ascending=False).iloc[0]
st.success(f"🏅 Highest Sales Month: {best_month['Date']} — ₹{int(best_month['TotalSale']):,}")
st.line_chart(monthly_sales.set_index('Date')['TotalSale'])

# 🗺️ Region Heatmap
st.subheader("🗺️ Region-wise Sales Heatmap")
region_sales = filtered_df.groupby('Region')['TotalSale'].sum().reset_index()
fig, ax = plt.subplots()
sns.barplot(x='Region', y='TotalSale', data=region_sales, palette="coolwarm", ax=ax)
st.pyplot(fig)

# ⬇️ Download Data
st.subheader("⬇️ Download Filtered Data")

csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("Download CSV", data=csv, file_name='filtered_sales.csv', mime='text/csv')

try:
    import xlsxwriter
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        filtered_df.to_excel(writer, index=False, sheet_name='SalesData')
    st.download_button(
        label="Download Excel",
        data=buffer,
        file_name='filtered_sales.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
except ImportError:
    st.warning("⚠️ Excel download not available. Run `pip install xlsxwriter` to enable.")
