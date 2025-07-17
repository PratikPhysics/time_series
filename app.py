import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import pickle
import yfinance as yf
from datetime import datetime
from pandas.tseries.offsets import DateOffset

# -----------------------------------------
# Streamlit Config
# -----------------------------------------
st.set_page_config(page_title="Gold Price Forecast (SARIMA)", layout="wide")
st.title("📈 Gold Price Forecast using SARIMA Model")

# -----------------------------------------
# Load Gold Data
# -----------------------------------------
@st.cache_data
def load_gold_data():
    df = yf.download("GC=F", start="2005-01-01", end="2025-07-01", interval="1mo")
    df = df[['Close']].copy()
    df.columns = ['Price']
    df.dropna(inplace=True)
    return df

# -----------------------------------------
# Load SARIMA Model
# -----------------------------------------
@st.cache_resource
def load_model(file_path):
    with open(file_path, "rb") as f:
        model = pickle.load(f)
    return model

# -----------------------------------------
# Forecast Function
# -----------------------------------------
def forecast_sarima(model, steps, last_date):
    forecast_values = model.forecast(steps=steps)
    forecast_index = pd.date_range(start=last_date + DateOffset(months=1), periods=steps, freq='M')
    forecast_df = pd.DataFrame({'Price': forecast_values}, index=forecast_index)
    return forecast_df

# -----------------------------------------
# Sidebar Controls
# -----------------------------------------
n_months = st.sidebar.slider("⏳ Forecast Months", 3, 24, 12)
start_date = st.sidebar.date_input("📆 View From", value=datetime(2020, 1, 1))
end_date = st.sidebar.date_input("📆 View To", value=datetime(2025, 1, 1))

# -----------------------------------------
# Load Everything
# -----------------------------------------
gold_data = load_gold_data()
model = load_model("sarima_gold_model.pkl")
forecast_df = forecast_sarima(model, n_months, gold_data.index[-1])

# Combine actual and forecast data
combined_df = pd.concat([gold_data, forecast_df])
combined_df.index.name = "Date"

# -----------------------------------------
# Apply Date Range Filter
# -----------------------------------------
filtered_df = combined_df[(combined_df.index.date >= start_date) & (combined_df.index.date <= end_date)]
historical = filtered_df[filtered_df.index <= gold_data.index[-1]]
forecasted = filtered_df[filtered_df.index > gold_data.index[-1]]

# -----------------------------------------
# Plotting
# -----------------------------------------
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(historical.index, historical['Price'], label="Historical", color="gold", linewidth=2)
if not forecasted.empty:
    ax.plot(forecasted.index, forecasted['Price'], label="Forecast", color="green", linestyle="--", linewidth=2)
ax.set_title("Gold Price Forecast using SARIMA")
ax.set_xlabel("Date")
ax.set_ylabel("Price (USD)")
ax.grid(True)
ax.legend()
st.pyplot(fig)

# -----------------------------------------
# Forecast Table
# -----------------------------------------
with st.expander("📄 View Forecasted Values"):
    st.dataframe(forecast_df.style.format({"Price": "{:.2f}"}))
