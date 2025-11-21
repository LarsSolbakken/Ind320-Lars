import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
# from utils import detect_outliers, detect_anomalies   # old import path
from utils.plots import detect_outliers, detect_anomalies


# =========================================================
# PAGE TITLE
# =========================================================
st.title("🌡️ Outlier & Anomaly Detection")


# =========================================================
# LOAD WEATHER DATA (must be fetched from Table page first)
# =========================================================
# The Table page loads the Open-Meteo weather dataset and stores it in:
#   st.session_state["df_weather"]
df_weather = st.session_state.get("df_weather")

if df_weather is None:
    # User cannot proceed until weather data is downloaded
    st.warning("No weather data found yet. Please visit the Table page first to download data.")
    st.stop()


# =========================================================
# DETERMINE SELECTED AREA & CITY
# =========================================================
# "selected_area" is set on the Electricity Production page (NO1–NO5)
area = st.session_state.get("selected_area", "NO5")

# Static mapping of price area → representative city
area2city = {
    "NO1": "Oslo",
    "NO2": "Kristiansand",
    "NO3": "Trondheim",
    "NO4": "Tromsø",
    "NO5": "Bergen"
}

# Primary city source: saved session value from Table page
# Fallback: infer from price area
city = st.session_state.get("selected_city", area2city.get(area, "Bergen"))

# Display to user which dataset they are analyzing
st.markdown(f"### 📍 Showing data for **{city} ({area})**")


# =========================================================
# CREATE TWO TABS: SPC Outliers & LOF Anomalies
# =========================================================
tab1, tab2 = st.tabs(["Temperature Outliers (SPC)", "Precipitation Anomalies (LOF)"])


# =========================================================
# TAB 1 — SPC OUTLIER DETECTION (Temp)
# =========================================================
with tab1:
    st.subheader("SPC-based Outlier Detection (Temperature)")

    # -----------------------------
    # USER CONTROLS
    # -----------------------------
    # DCT cutoff controls smoothness of the seasonal baseline.
    cutoff = st.slider(
        "DCT frequency cutoff (smoothness)",
        min_value=20,
        max_value=300,
        value=100,
        help=(
            "Lower cutoff → smoother seasonal trend (more deviations flagged).\n"
            "Higher cutoff → more wiggle in trend (fewer points flagged)."
        )
    )

    # std_mult controls SPC control-limit width.
    std_mult = st.slider(
        "SPC threshold multiplier (strictness)",
        min_value=1.0,
        max_value=4.0,
        value=2.0,
        step=0.1,
        help=(
            "Lower value → narrower control limits → more outliers.\n"
            "Higher value → wider control limits → fewer outliers."
        )
    )

    # -----------------------------
    # RUN SPC + DCT OUTLIER DETECTION
    # -----------------------------
    # detect_outliers() returns:
    #   - fig: Plotly figure showing SATV + control limits + outliers
    #   - summary: numeric summary (counts, thresholds, etc.)
    #   - thresholds: exact upper/lower SPC bounds
    fig, summary, thresholds = detect_outliers(
        df_weather["temperature_2m (°C)"],
        cutoff=cutoff,
        std_mult=std_mult
    )

    # Display interactive SPC figure
    st.plotly_chart(fig, use_container_width=True)

    # Show numerical result summary
    st.write("Summary:", summary)



# =========================================================
# TAB 2 — LOF ANOMALY DETECTION (Precip)
# =========================================================
with tab2:
    st.subheader("LOF-based Anomaly Detection (Precipitation)")

    # -----------------------------
    # USER CONTROLS
    # -----------------------------
    contamination = st.slider(
        "Expected anomaly proportion (contamination)",
        min_value=0.001,
        max_value=0.0500,
        value=0.0100,
        step=0.001,
        format="%.3f",
        help=(
            "Controls how many points LOF marks as anomalies.\n"
            "Higher value → more anomalies detected."
        )
    )

    # -----------------------------
    # RUN LOF ANOMALY DETECTION
    # -----------------------------
    # detect_anomalies returns:
    #   - fig: interactive plot
    #   - summary: detection statistics
    #   - anomalies: list of anomaly timestamps
    fig, summary, anomalies = detect_anomalies(
        df_weather["precipitation (mm)"],
        proportion=contamination
    )

    # Render the LOF plot and summary
    st.plotly_chart(fig, use_container_width=True)
    st.write("Summary:", summary)
