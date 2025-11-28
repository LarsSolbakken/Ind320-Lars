import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Weather loader (ERA5/OpenMeteo style hourly data)
from utils.weather import load_weather_range

# Snow drift computation utilities (provided in utils/Snow_drift.py)
from utils.Snow_drift import (
    compute_yearly_results,
    compute_average_sector,
    plot_rose,
    compute_fence_height
)


# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(page_title="Snow drift & wind rose", layout="wide")
st.title("❄️ Snow drift and wind rose")


# =========================================================
# REQUIRE MAP COORDINATE FROM MAP PAGE
# =========================================================
# The Map page stores the clicked coordinate into session_state["last_pin"].
if "last_pin" not in st.session_state:
    st.error("No coordinate selected on the map page. Go to 'Map & Area Analysis' and click a point.")
    st.stop()

# Extract latitude/longitude from Map page state
lat, lon = st.session_state.last_pin
st.write(f"Selected coordinate: {lat:.4f}°N, {lon:.4f}°E")


# =========================================================
# SELECT YEAR RANGE FOR WEATHER DOWNLOAD
# =========================================================
download_start, download_end = st.slider(
    "Select year range",
    min_value=1980,
    max_value=2024,
    value=(2020, 2023)
)

# Load multi-year ERA5/Open-Meteo data using a utility function
df_weather = load_weather_range(lat, lon, download_start, download_end)


# =========================================================
# PARAMETERS FOR SNOW TRANSPORT MODEL
# =========================================================
# These are fixed parameters used in the Qₜ computation.
# They can later be made user-selectable if desired.
T = 3000     # Maximum transport distance (m)
F = 30000    # Fetch (m)
theta = 0.5  # Relocation coefficient


# =========================================================
# SELECT METEOROLOGICAL SEASONS (JULY 1 → JUNE 30)
# =========================================================
seasons_available = sorted(df_weather["season"].unique())

st.subheader("Season (year) selection")

# The season system (e.g., 2020 corresponds to July 2020 – June 2021)
season_start, season_end = st.select_slider(
    "Select season range (season = July 1–June 30)",
    options=seasons_available,
    value=(seasons_available[0], seasons_available[-1]),
)

st.write(f"Using seasons {season_start}–{season_end} (each is July–June).")

# Filter weather data to selected seasons only
mask = (df_weather["season"] >= season_start) & (df_weather["season"] <= season_end)
df_sel = df_weather.loc[mask].copy()

if df_sel.empty:
    st.warning("No meteorological data for this year range.")
    st.stop()


# =========================================================
# 5. CALCULATE SNOW DRIFT PER YEAR (Qₜ)
# =========================================================
# Compute Qₜ per season using utils/Snow_drift.py
yearly_all = compute_yearly_results(df_sel, T, F, theta)

# Average seasonal Qₜ across selected seasons
overall_avg_Qt = yearly_all["Qt (kg/m)"].mean()

# Display results
yearly_display = yearly_all.copy()
yearly_display["Qt (tonnes/m)"] = yearly_display["Qt (kg/m)"] / 1000

st.subheader("Yearly snow drift (Qt)")
st.dataframe(
    yearly_display[["season", "Qt (tonnes/m)", "Control"]].style.format(
        {"Qt (tonnes/m)": "{:.1f}"}
    )
)


# =========================================================
# BAR CHART OF SNOW DRIFT PER SEASON
# =========================================================
fig_bar = go.Figure()
fig_bar.add_trace(
    go.Bar(
        x=yearly_all["season"].astype(str),
        y=yearly_all["Qt (kg/m)"] / 1000,               # convert to tonnes/m
        text=[f"{v:.1f}" for v in yearly_all["Qt (kg/m)"] / 1000],
        textposition="outside"
    )
)
fig_bar.update_layout(
    title="Annual snow drift per season",
    xaxis_title="Season (start year)",
    yaxis_title="Qt [tonnes/m]",
    height=350
)

st.plotly_chart(fig_bar, use_container_width=True)


# =========================================================
# 6. WIND ROSE (DIRECTIONAL SNOW TRANSPORT)
# =========================================================
st.subheader("Wind rose (directional snow transport)")

# Compute directional average transport per sector
avg_sectors = compute_average_sector(df_sel)

num_sectors = 16
angles_deg = np.arange(0, 360, 360/num_sectors)

fig_rose = go.Figure()
fig_rose.add_trace(
    go.Barpolar(
        r=avg_sectors / 1000,          # convert to tonnes/m
        theta=angles_deg,
        width=[360/num_sectors] * num_sectors,
        marker_line_color="black",
        marker_line_width=1,
        hovertemplate="<b>%{theta}°</b><br>Qt = %{r:.1f} tonnes/m<extra></extra>"
    )
)

fig_rose.update_layout(
    polar=dict(
        radialaxis=dict(title="Qt [tonnes/m]", visible=True)
    ),
    title=f"Average directional transport • Overall Qt ≈ {overall_avg_Qt/1000:.2f} tonnes/m",
    height=600
)

st.plotly_chart(fig_rose, use_container_width=True)


# =========================================================
# 7. OPTIONAL: FENCE HEIGHT ESTIMATION
# =========================================================
st.subheader("Estimated fence height (optional)")

# Fence type → scaling rules are in compute_fence_height()
fence_type = st.selectbox(
    "Fence type", ["Wyoming", "Slat-and-wire", "Solid"]
)

# Compute a representative fence height for average seasonal Qₜ
H_overall = compute_fence_height(overall_avg_Qt, fence_type)

st.write(
    f"Approximate effective fence height for overall average Qt: "
    f"**{H_overall:.1f} m** ({fence_type})"
)
