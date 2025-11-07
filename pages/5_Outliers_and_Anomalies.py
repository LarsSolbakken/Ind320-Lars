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
     # --- User controls ---
    cutoff = st.slider(
        "DCT frequency cutoff (smoothness)",
        min_value=20,
        max_value=300,
        value=100,   # default
        help="Lower = smoother seasonal trend (more outliers). Higher = more fluctuation (fewer outliers)."
    )
    std_mult = st.slider(
        "SPC threshold multiplier (strictness)",
        min_value=1.0,
        max_value=4.0,
        value=2.0,
        step=0.1,
        help="Lower = stricter limits (more outliers). Higher = wider limits (fewer outliers)."
    )
    # Run SPC + DCT outlier detection function from utils.py
    # --- Run detection with user-selected parameters ---
    fig, summary, thresholds = detect_outliers(df_weather["temperature_2m"],
        cutoff=cutoff,
        std_mult=std_mult)
    # Display resulting plot
    st.pyplot(fig)
    # Display numeric summary of outliers
    st.write("Summary:", summary)

# --- Tab 2: LOF Anomaly Detection (Precipitation) ---
with tab2:
    st.subheader("LOF-based Anomaly Detection (Precipitation)")
    contamination = st.slider(
        "Expected anomaly proportion (contamination)",
        min_value=0.001, max_value=0.0500, value=0.0100, step=0.001, format="%.3f",
        help="Amount of data expected to be anomalies. Higher = more anomalies detected."
    )
    # Run Local Outlier Factor anomaly detection
    fig, summary, anomalies = detect_anomalies(df_weather["precipitation"], proportion=contamination)
    # Show the plot and summary
    st.pyplot(fig)
    st.write("Summary:", summary)
