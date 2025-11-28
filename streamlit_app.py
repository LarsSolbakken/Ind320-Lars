import streamlit as st; 


import streamlit as st

st.set_page_config(page_title="IND320 • Home", layout="wide")

st.title("🏠 IND320 — Energy & Meteorology Explorer")

st.markdown("""
Welcome to your IND320 project app.

Use the sidebar to navigate through:
- **Map & Area Analysis**
- **Electricity Production**
- **Electricity Consumption**
- **Exploratory Data Analysis (Tables, Plots, STL, Anomalies)**
- **Meteorology ↔ Production Correlation**
- **Forecasting (SARIMAX)**
- **Snow Drift Modelling**

This app integrates:
- Elhub production & consumption data (2021–2024)
- Open-Meteo weather data
- Statistical analyses
- Time-series decomposition
- Forecasting
- Snow transport physics


""")
