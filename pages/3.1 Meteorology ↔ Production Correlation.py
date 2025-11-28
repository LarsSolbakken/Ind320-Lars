import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from utils.weather import download_weather2


# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(page_title="Sliding Window Correlation", layout="wide")
st.title("📈 Sliding Window Correlation: Weather vs Energy")

# Predefined representative coordinates for each price area
# These ensure weather is taken from the central city of that area
area_coords = {
    "NO1": (59.91, 10.75),   # Oslo
    "NO2": (58.15, 8.00),    # Kristiansand
    "NO3": (63.43, 10.39),   # Trondheim
    "NO4": (69.65, 18.96),   # Tromsø
    "NO5": (60.39, 5.33),    # Bergen
}


# =========================================================
# REQUIRE SELECTED AREA FROM OTHER PAGES
# =========================================================
# The map page sets last_pin, and the Production/Consumption pages
# store selected_area into session_state.
if "last_pin" not in st.session_state:
    # We still check last_pin so the user must visit the map page first.
    st.error("No coordinate selected on the map page. Please choose a point.")
    st.stop()

# Instead of using the exact clicked coordinate, we now use
# the representative city of the selected price area.
area = st.session_state.get("selected_area", "NO1")
lat, lon = area_coords[area]

st.write(f"Using representative weather location for {area}: {lat:.4f}°N, {lon:.4f}°E")


# =========================================================
# LOAD WEATHER DATA (Open-Meteo)
# =========================================================
with st.spinner("Loading meteorology data…"):
    # Download hourly weather for the selected location and year
    df_weather = download_weather2(lon, lat, 2023).copy()

    # Move index into a normal column for merging later
    df_weather["time"] = df_weather.index
    df_weather = df_weather.reset_index(drop=True)

    # Standardize column names for consistency through the app
    df_weather = df_weather.rename(columns={
        "temperature_2m (°C)": "temperature_2m",
        "precipitation (mm)": "precipitation",
        "wind_speed_10m (m/s)": "wind_speed_10m",
        "wind_direction_10m (°)": "wind_direction_10m",
    })


# =========================================================
# SELECT ENERGY KIND (Production or Consumption)
# =========================================================
st.subheader("Energy kind")
energy_kind = st.radio(
    "Select energy dataset",
    ["Production", "Consumption"],
    horizontal=True
)


# =========================================================
# LOAD SELECTED ENERGY DATA
# =========================================================
# Data is stored in session_state by the corresponding pages.
if energy_kind == "Production":
    if "elhub_data" not in st.session_state:
        st.error("Production data missing — load it on the Production page first.")
        st.stop()
    df_energy = st.session_state["elhub_data"].copy()
else:
    if "consumption_data" not in st.session_state:
        st.error("Consumption data missing — load it on the Consumption page first.")
        st.stop()
    df_energy = st.session_state["consumption_data"].copy()


# =========================================================
# CLEAN & PREPARE ENERGY DATAFRAME
# =========================================================
# Rename timestamp column for consistency
df_energy = df_energy.rename(columns={"starttime": "time"})
df_energy["time"] = pd.to_datetime(df_energy["time"], errors="coerce")

# Consumption group names are renamed to avoid clashes with production names
if "consumptiongroup" in df_energy.columns:
    df_energy["consumptiongroup"] = df_energy["consumptiongroup"].astype(str) + "_cons"

# Pivot long energy data into wide form: one column per group
pivot_col = "productiongroup" if "productiongroup" in df_energy.columns else "consumptiongroup"

df_energy_wide = df_energy.pivot_table(
    index="time",
    columns=pivot_col,
    values="quantitykwh",
    aggfunc="sum"
).reset_index()


# =========================================================
# MERGE WEATHER + ENERGY ON TIMESTAMP
# =========================================================
df = df_weather.merge(df_energy_wide, on="time", how="inner").sort_values("time")


# =========================================================
# VARIABLE SELECTION (weather vs energy)
# =========================================================
# Available meteorological variables
meteo_vars = ["temperature_2m", "precipitation", "wind_speed_10m", "wind_direction_10m"]

# All other columns except time + weather = energy groups
energy_vars = [c for c in df.columns if c not in ["time"] + meteo_vars]

# Sort energy variables but push "other" columns to the end for readability
energy_vars = sorted(energy_vars, key=lambda x: ("other" in x.lower(), x))

# Two dropdowns for selecting what to correlate
col1, col2 = st.columns(2)
with col1:
    meteo = st.selectbox("Meteorological variable", meteo_vars)
with col2:
    energy = st.selectbox("Energy variable", energy_vars)


# =========================================================
# LAG + ROLLING WINDOW SETTINGS
# =========================================================
# Lag shifts weather variable forward/backward in time (in hours)
lag = st.slider("Lag (hours)", -48, 48, 0)

# Rolling window controls the smoothing of correlation
window = st.slider("Window length (hours)", 6, 336, 72)


# =========================================================
# COMPUTE ROLLING CORRELATION
# =========================================================
# Apply lag to meteorology variable
df["meteo_shifted"] = df[meteo].shift(lag)

# Rolling Pearson correlation between shifted weather and selected energy variable
df["corr"] = (
    df["meteo_shifted"]
    .rolling(window)
    .corr(df[energy])
)


# =========================================================
# CORRELATION PLOT
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
    xaxis_title="Time"
)

st.plotly_chart(fig, use_container_width=True)


# =========================================================
# NORMALIZED COMPARISON PLOT (Z-score)
# =========================================================
st.subheader("Normalized comparison of meteorology and energy signals")

# Z-score normalization to compare variables on the same scale
def zscore(x):
    if x.std() == 0:           # Avoid division-by-zero errors
        return x - x.mean()
    return (x - x.mean()) / x.std()

# Normalize both selected series
df["meteo_norm"] = zscore(df["meteo_shifted"])
df["energy_norm"] = zscore(df[energy])

# Combined plot showing both normalized series
fig_norm = px.line(
    df,
    x="time",
    y=["meteo_norm", "energy_norm"],
    labels={"value": "Z-score", "variable": "Series"},
    title=f"Normalized comparison: {meteo} vs {energy}",
    height=400,
)

fig_norm.update_layout(legend_title_text="Series")

st.plotly_chart(fig_norm, use_container_width=True)


# =========================================================
# USER HINT
# =========================================================
st.info(
    "Try adjusting lag and window size. "
    "Large deviations often correspond to storms or high-wind events."
)
