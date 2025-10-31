import streamlit as st
import matplotlib.pyplot as plt
from utils import detect_outliers, detect_anomalies, download_weather

# --- Page title ---
st.title("🌡️ Outlier & Anomaly Detection")

# --- Load or fetch weather data from session state ---
# Weather data should have been downloaded earlier on the Table page.
df_weather = st.session_state.get("df_weather")

if df_weather is None:
    # Stop execution if no data available — user must go back and download it first
    st.warning("No weather data found yet. Please visit the Table page first to download data.")
    st.stop()

# --- Determine which city/area data belongs to ---
# The price area (NO1–NO5) was selected on the Electricity Production page.
area = st.session_state.get("selected_area", "NO5")

# Map each price area to its representative city
area2city = {"NO1": "Oslo", "NO2": "Kristiansand", "NO3": "Trondheim", "NO4": "Tromsø", "NO5": "Bergen"}

# Retrieve selected city from session, or infer it from the area
city = st.session_state.get("selected_city", area2city.get(area, "Bergen"))

# Display current selection to user
st.markdown(f"### 📍 Showing data for **{city} ({area})**")

# --- Create two analysis tabs ---
tab1, tab2 = st.tabs(["Temperature Outliers (SPC)", "Precipitation Anomalies (LOF)"])

# --- Tab 1: SPC Outlier Detection (Temperature) ---
with tab1:
    st.subheader("SPC-based Outlier Detection (Temperature)")
    # Run SPC + DCT outlier detection function from utils.py
    fig, summary, thresholds = detect_outliers(df_weather["temperature_2m"])
    # Display resulting plot
    st.pyplot(fig)
    # Display numeric summary of outliers
    st.write("Summary:", summary)

# --- Tab 2: LOF Anomaly Detection (Precipitation) ---
with tab2:
    st.subheader("LOF-based Anomaly Detection (Precipitation)")
    # Run Local Outlier Factor anomaly detection
    fig, summary, anomalies = detect_anomalies(df_weather["precipitation"])
    # Show the plot and summary
    st.pyplot(fig)
    st.write("Summary:", summary)
