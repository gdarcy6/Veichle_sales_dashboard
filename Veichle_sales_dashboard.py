import streamlit as st
import pandas as pd
import plotly.express as px

# Load Data
def load_data():
    df = pd.read_csv("car_prices.csv")  # file path
    
    # Convert numeric columns to appropriate types
    df['year'] = pd.to_numeric(df['year'], errors='coerce')
    df['sellingprice'] = pd.to_numeric(df['sellingprice'], errors='coerce')
    df['mmr'] = pd.to_numeric(df['mmr'], errors='coerce')
    
    # Ensure 'saledate' is in datetime format and convert to UTC-naive
    df['saledate'] = pd.to_datetime(df['saledate'], errors='coerce', utc=True)
    df['saledate'] = df['saledate'].dt.tz_localize(None)  # Make it naive
    
    # Drop or fill NaN values if necessary
    df.dropna(inplace=True)  # You could also use df.fillna(0)
    
    return df

df = load_data()

# Calculate Total Sales (Static - Full Dataset)
total_cars_sold = len(df)  # Total number of cars sold

# Streamlit App Configuration
st.set_page_config(page_title="Vehicle Sales Dashboard", layout="wide")
st.title("🚗 Vehicle Sales and Market Trends Dashboard")
st.markdown("<h3 style='font-size: 18px;'>Car sales in the United States 2014-15</h3>", unsafe_allow_html=True)

# Display Total Cars Sold at the Top
st.metric("Total Cars Sold (2014-15)", f"{total_cars_sold:,}")

# Sidebar Filters
st.sidebar.header("Filter Options")
year_options = sorted(df['year'].unique())
brand_options = sorted(df['make'].unique())
state_options = sorted(df['state'].unique())

year_filter = st.sidebar.multiselect("Select Model Year", options=year_options, default=[])
brand_filter = st.sidebar.multiselect("Select Brand", options=brand_options, default=[])
state_filter = st.sidebar.multiselect("Select State", options=state_options, default=[])

# Apply Filters
df_filtered = df.copy()
if year_filter:
    df_filtered = df_filtered[df_filtered['year'].isin(year_filter)]
if brand_filter:
    df_filtered = df_filtered[df_filtered['make'].isin(brand_filter)]
if state_filter:
    df_filtered = df_filtered[df_filtered['state'].isin(state_filter)]

# KPI Metrics
avg_price = df_filtered['sellingprice'].mean()
avg_mmr = df_filtered['mmr'].mean()
total_sales_filtered = df['sellingprice'].sum()  # Total revenue from all sales

col1, col2, col3 = st.columns(3)
col1.metric("Average Selling Price", f"${avg_price:,.2f}")
col2.metric("Average MMR Value", f"${avg_mmr:,.2f}")
col3.metric("Total Sales (Filtered)", f"${total_sales_filtered:,}")

# Price Trends Over Time (Smoothed)
df_filtered['saledate'] = pd.to_datetime(df_filtered['saledate'])
df_filtered = df_filtered.sort_values('saledate')

# Apply a rolling mean for smoothing (30-day window)
df_filtered['rolling_avg_price'] = df_filtered.groupby('make')['sellingprice'].transform(lambda x: x.rolling(window=30, min_periods=1).mean())

# Smoothed line chart
fig1 = px.line(df_filtered, x='saledate', y='rolling_avg_price', color='make', title="Smoothed Price Trends Over Time")
st.plotly_chart(fig1, use_container_width=True)

# Sales Distribution by Brand
fig2 = px.bar(df_filtered, x='make', y='sellingprice', title="Sales Distribution by Brand", color='make')
st.plotly_chart(fig2, use_container_width=True)

# Condition-Based Price Analysis
fig3 = px.box(df_filtered, x='condition', y='sellingprice', title="Condition-Based Price Analysis", color='condition')
st.plotly_chart(fig3, use_container_width=True)

# Heatmap of Sales by State
sales_by_state = df_filtered.groupby('state', as_index=False)['sellingprice'].sum()
sales_by_state['state'] = sales_by_state['state'].str.upper()  # Ensure state codes are uppercase

fig4 = px.choropleth(
    sales_by_state,
    locations='state',
    locationmode='USA-states',
    color='sellingprice',
    color_continuous_scale='blues',
    scope="usa",
    title="Total Sales by State")
st.plotly_chart(fig4, use_container_width=True)

st.sidebar.markdown("### Dataset Preview")
st.sidebar.dataframe(df_filtered.head())
