import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
# from utils import download_weather2     
from utils.weather import download_weather2


# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(page_title="Sliding Window Correlation", layout="wide")
st.title("📈 Sliding Window Correlation: Weather vs Energy")


# =========================================================
# REQUIRE A COORDINATE FROM THE MAP PAGE
# =========================================================
# The user clicks a point on the Price Area Map.
# That coordinate is stored in st.session_state["last_pin"].
if "last_pin" not in st.session_state:
    st.error("No coordinate selected on the map page. Please choose a point.")
    st.stop()

lat, lon = st.session_state["last_pin"]
st.write(f"Using coordinate: {lat:.4f}°N  {lon:.4f}°E")


# =========================================================
# LOAD WEATHER + ENERGY DATA
# =========================================================
with st.spinner("Loading meteorology and energy data…"):

    # -----------------------------------------------------
    # 1) METEOROLOGY (Open-Meteo) — cached in utils.weather
    # -----------------------------------------------------
    df_weather = download_weather2(lon, lat, 2023).copy()

    # download_weather2 returns a DataFrame indexed by time.
    # Convert index → column so merging becomes easier.
    df_weather["time"] = df_weather.index
    df_weather = df_weather.reset_index(drop=True)

    # Standardize column names for consistent processing later
    df_weather = df_weather.rename(columns={
        "temperature_2m (°C)": "temperature_2m",
        "precipitation (mm)": "precipitation",
        "wind_speed_10m (m/s)": "wind_speed_10m",
        "wind_direction_10m (°)": "wind_direction_10m",
    })

    # -----------------------------------------------------
    # 2) ENERGY (production + consumption) — from MongoDB
    # -----------------------------------------------------
    if "elhub_data" not in st.session_state:
        st.error("❌ No energy data found. Go to the Electricity Production page first.")
        st.stop()

    df_energy = st.session_state["elhub_data"].copy()

    # Unify timestamp column so weather+energy can be merged
    df_energy = df_energy.rename(columns={"starttime": "time"})
    df_energy["time"] = pd.to_datetime(df_energy["time"], errors="coerce")

    # Pivot production OR consumption group columns into wide format:
    # Each group becomes one column containing kWh values per hour.
    df_energy_wide = df_energy.pivot_table(
        index="time",
        columns="productiongroup" if "productiongroup" in df_energy.columns else "consumptiongroup",
        values="quantitykwh",
        aggfunc="sum"
    )

    # If dataset contains consumption data, pivot and join as well
    if "consumptiongroup" in df_energy.columns:
        df_cons_wide = df_energy.pivot_table(
            index="time",
            columns="consumptiongroup",
            values="quantitykwh",
            aggfunc="sum"
        )
        df_energy_wide = df_energy_wide.join(df_cons_wide, how="outer")

    # Reset index to turn "time" into a normal column
    df_energy_wide = df_energy_wide.reset_index()
    df_energy_wide.columns.name = None

    # -----------------------------------------------------
    # 3) MERGE WEATHER + ENERGY ON TIMESTAMP
    # -----------------------------------------------------
    df = df_weather.merge(df_energy_wide, on="time", how="inner")
    df = df.sort_values("time")


# =========================================================
# VARIABLE SELECTION (Weather vs Energy)
# =========================================================
# Meteorological variables available from Open-Meteo
meteo_vars = ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"]

# Everything else = energy variables (production + consumption groups)
energy_vars = [c for c in df.columns if c not in ["time"] + meteo_vars]

col1, col2 = st.columns(2)
with col1:
    meteo = st.selectbox("Meteorological variable", meteo_vars)
with col2:
    energy = st.selectbox("Energy variable (production & consumption)", energy_vars)


# =========================================================
# LAG AND WINDOW SETTINGS
# =========================================================
# Lag units = hours.
# Negative lag: weather leads energy
# Positive lag: energy follows weather
lag = st.slider("Lag (hours)", -48, 48, 0)

# Rolling window determines smoothing of the correlation curve
window = st.slider("Window length (hours)", 6, 336, 72)


# =========================================================
# APPLY LAG + ROLLING CORRELATION
# =========================================================
# Shift meteorological variable forward/backward in time
df["meteo_shifted"] = df[meteo].shift(lag)

# Compute rolling Pearson correlation between:
#    shifted meteorology vs energy variable
df["corr"] = (
    df["meteo_shifted"]
    .rolling(window)
    .corr(df[energy])
)


# =========================================================
# INTERACTIVE PLOTLY FIGURE
# =========================================================
fig = px.line(
    df,
    x="time",
    y="corr",
    title=f"Rolling Correlation: {meteo} → {energy} (lag={lag}h, window={window}h)",
    height=500,
)

fig.update_layout(
    yaxis_title="Correlation",
    xaxis_title="Time",
)

st.plotly_chart(fig, use_container_width=True)

# Extra hint to guide user exploration
st.info(
    "Try adjusting **lag** and **window size**. "
    "Observe how correlation changes during storms or weather extremes."
)
