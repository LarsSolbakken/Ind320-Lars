import streamlit as st
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import plotly.graph_objects as go

# from utils import download_weather2
from utils.weather import download_weather2
# (download_weather2 pulls hourly weather and is cached)


# =========================================================
# PAGE CONFIGURATION
# =========================================================
st.set_page_config(page_title="SARIMAX Forecast", layout="wide")
st.title("📈 SARIMAX Forecast: Energy Production / Consumption")


# =========================================================
# 0. LOAD ENERGY DATA FROM SESSION (from Production page)
# =========================================================
if "elhub_data" not in st.session_state:
    st.error(
        "❌ No energy data loaded.\n\n"
        "Go to the **Electricity Production** page first so we can load MongoDB data."
    )
    st.stop()

df_raw = st.session_state["elhub_data"].copy()

# Clean timestamps for time-series modelling
df_raw["starttime"] = pd.to_datetime(df_raw["starttime"], errors="coerce")
df_raw = df_raw.dropna(subset=["starttime"]).sort_values("starttime")


# =========================================================
# 1. SELECT PRICE AREA → BUILD WIDE ENERGY TABLE
# =========================================================
st.subheader("1️⃣ Select price area and target variable")

# Unique areas available
areas = sorted(df_raw["pricearea"].unique())
if not areas:
    st.error("No price areas found in the data.")
    st.stop()

# Default saved from earlier pages
default_area = st.session_state.get("selected_area", areas[0])
if default_area not in areas:
    default_area = areas[0]

selected_area = st.selectbox("Price area", areas, index=areas.index(default_area))
st.session_state["selected_area"] = selected_area

# Filter dataset to the selected price area
df_area = df_raw[df_raw["pricearea"] == selected_area].copy()

# Convert long → wide: one production group per column
df_wide = (
    df_area.pivot_table(
        index="starttime",
        columns="productiongroup",
        values="quantitykwh",
        aggfunc="sum",
    )
    .asfreq("H")   # ensure strict hourly indexing
    .sort_index()
)

energy_vars = df_wide.columns.tolist()
if not energy_vars:
    st.error("No production groups found for this price area.")
    st.stop()


# =========================================================
# 2. WEATHER SETUP (OPTIONAL EXOG = bonus variables)
# =========================================================
st.subheader("2️⃣ Weather as optional exogenous regressors")

# Mapping price area → (city, lat, lon)
area2loc = {
    "NO1": ("Oslo",         59.91, 10.75),
    "NO2": ("Kristiansand", 58.15,  8.00),
    "NO3": ("Trondheim",    63.43, 10.39),
    "NO4": ("Tromsø",       69.65, 18.96),
    "NO5": ("Bergen",       60.39,  5.33),
}

city, lat, lon = area2loc.get(selected_area, ("Oslo", 59.91, 10.75))
st.write(f"Weather will be pulled from **{city}** (lat={lat}, lon={lon}).")

# Expected weather columns returned by download_weather2
WEATHER_VARS = [
    "temperature_2m (°C)",
    "precipitation (mm)",
    "wind_speed_10m (m/s)",
    "wind_direction_10m (°)",
]


# Cached function downloading weather for all years used in the model index
@st.cache_data(show_spinner=False)
def get_weather_for_index(selected_area: str, _index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Download weather for all calendar years present in the model index,
    then align it exactly to the hourly DatetimeIndex used by the energy data.
    """
    city, lat, lon = area2loc.get(selected_area, ("Oslo", 59.91, 10.75))

    years = sorted(set(_index.year))
    dfs = []

    for year in years:
        df_w = download_weather2(lon, lat, int(year))
        df_w = df_w.copy()
        df_w.index = pd.to_datetime(df_w.index)
        df_w = df_w.sort_index()
        dfs.append(df_w)

    # Combine all years and remove duplicate timestamps
    df_weather_all = pd.concat(dfs, axis=0)
    df_weather_all = df_weather_all[~df_weather_all.index.duplicated(keep="first")]

    # Keep only variables that actually exist in the downloaded dataset
    cols_existing = [c for c in WEATHER_VARS if c in df_weather_all.columns]
    df_weather_all = df_weather_all[cols_existing]

    # Align completely to the energy index (same timestamps)
    df_weather_all = df_weather_all.asfreq("H")
    df_weather_all = df_weather_all.reindex(_index)

    return df_weather_all


# =========================================================
# 3. SELECT TARGET + EXOGENOUS VARIABLES
# =========================================================
st.subheader("3️⃣ Select target and exogenous variables")

col1, col2 = st.columns(2)

with col1:
    target = st.selectbox("Target energy variable to forecast", energy_vars)

with col2:
    energy_exog_candidates = [c for c in energy_vars if c != target]
    exog_selected_energy = st.multiselect(
        "Energy exogenous variables",
        options=energy_exog_candidates,
        default=[],
    )

# Weather exogenous variables — optional, more advanced
selected_weather_exog = st.multiselect(
    "Weather exogenous variables (bonus)",
    options=WEATHER_VARS,
    default=[],
    help="If selected, weather data will be downloaded for the same time index."
)

# Target series alone
y = df_wide[target].copy()


# =========================================================
# 4. TRAINING WINDOW AND FORECAST HORIZON
# =========================================================
st.subheader("4️⃣ Training period & forecast horizon")

min_time = y.index.min()
max_time = y.index.max()

if pd.isna(min_time) or pd.isna(max_time):
    st.error("Time index is invalid.")
    st.stop()

c1, c2 = st.columns(2)

with c1:
    train_start = st.date_input(
        "Training start",
        value=min_time.date(),
        min_value=min_time.date(),
        max_value=(max_time - pd.Timedelta(days=1)).date(),
    )
with c2:
    train_end = st.date_input(
        "Training end",
        value=(max_time - pd.Timedelta(days=7)).date(),
        min_value=train_start,
        max_value=(max_time - pd.Timedelta(days=1)).date(),
    )

# Forecast horizon (until how far into future to predict)
horizon = st.slider(
    "Forecast horizon (hours)",
    min_value=24,
    max_value=168,
    value=72,
    step=24,
)

# Convert to Timestamps
train_start = pd.to_datetime(train_start)
train_end = pd.to_datetime(train_end)

# Select training subset
mask_train = (y.index >= train_start) & (y.index <= train_end)
y_train = y.loc[mask_train]

if y_train.empty:
    st.error("Training window contains no data. Try adjusting the dates.")
    st.stop()

# Future timestamps after training end
future_index_all = y.index[y.index > train_end]
if future_index_all.empty:
    st.error("No future data available after the chosen training end.")
    st.stop()

future_index = future_index_all[:horizon]
y_future_actual = y.loc[future_index]


# =========================================================
# 5. BUILD EXOGENOUS MATRICES (energy + optional weather)
# =========================================================
st.subheader("5️⃣ SARIMAX parameters & exogenous matrix")

# Start with energy exog variables
df_exog_all = None
if exog_selected_energy:
    df_exog_all = df_wide[exog_selected_energy].copy()

# If weather exog selected → download matching weather values
if selected_weather_exog:
    with st.spinner("Downloading and aligning weather data…"):
        df_weather_full = get_weather_for_index(selected_area, y.index)

    # Keep only selected weather variables
    weather_cols = [c for c in selected_weather_exog if c in df_weather_full.columns]
    df_weather_sel = df_weather_full[weather_cols]

    # Combine with existing exog (if any)
    if df_exog_all is None:
        df_exog_all = df_weather_sel
    else:
        df_exog_all = df_exog_all.join(df_weather_sel, how="left")

# Clean and fill exog matrix (SARIMAX cannot handle NaNs)
if df_exog_all is not None:
    # Remove empty columns
    cols_before = df_exog_all.columns.tolist()
    df_exog_all = df_exog_all.dropna(axis=1, how="all")
    cols_after = df_exog_all.columns.tolist()

    removed = set(cols_before) - set(cols_after)
    if removed:
        st.warning(
            "The following exogenous variables had no data and were removed: "
            + ", ".join(sorted(removed))
        )

    # Fill missing values: forward-fill → back-fill
    df_exog_all = df_exog_all.ffill().bfill()

# Create exogenous matrices for train + forecast windows
if df_exog_all is not None:
    X_train = df_exog_all.loc[mask_train]
    X_future = df_exog_all.loc[future_index]
    all_exog_names = list(df_exog_all.columns)
else:
    X_train = None
    X_future = None
    all_exog_names = []


# =========================================================
# SARIMAX PARAMETER SELECTION
# =========================================================
with st.expander("Configure SARIMAX (p, d, q, P, D, Q, s)", expanded=True):
    c1, c2, c3 = st.columns(3)

    with c1:
        p = st.number_input("p (AR order)", 0, 5, 1)
        d = st.number_input("d (diff. order)", 0, 2, 0)
        q = st.number_input("q (MA order)", 0, 5, 1)

    with c2:
        P = st.number_input("P (seasonal AR)", 0, 3, 1)
        D = st.number_input("D (seasonal diff.)", 0, 2, 0)
        Q = st.number_input("Q (seasonal MA)", 0, 3, 1)

    with c3:
        s = st.selectbox("Season length s", [24, 168], index=0)

st.write(
    f"Model: **SARIMAX({p},{d},{q}) × ({P},{D},{Q})[{s}]** "
    f"with **{len(all_exog_names)}** exogenous regressors."
)


# =========================================================
# 6. FIT & FORECAST
# =========================================================
run = st.button("🚀 Run SARIMAX Forecast")

if run:

    # ---------- Train model ----------
    with st.spinner("Training SARIMAX…"):
        try:
            model = SARIMAX(
                y_train,
                order=(p, d, q),
                seasonal_order=(P, D, Q, s),
                exog=X_train,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            results = model.fit(disp=False)

        except Exception as e:
            st.error(f"Model fit failed: {e}")
            st.stop()

    # ---------- Forecast ----------
    with st.spinner("Forecasting…"):
        try:
            steps = len(future_index)
            forecast_res = results.get_forecast(steps=steps, exog=X_future)

            mean_forecast = forecast_res.predicted_mean
            conf_int = forecast_res.conf_int()

        except Exception as e:
            st.error(f"Forecast failed: {e}")
            st.stop()

    # Build forecast dataframe (with CI)
    lower = conf_int.iloc[:, 0]
    upper = conf_int.iloc[:, 1]

    df_plot = pd.DataFrame({
        "actual": y_future_actual,
        "forecast": mean_forecast,
        "lower": lower,
        "upper": upper,
    })


    # =====================================================
    # 7. PLOT FORECAST RESULTS
    # =====================================================
    st.subheader("6️⃣ Forecast Result")

    fig = go.Figure()

    # Training data
    fig.add_trace(go.Scatter(
        x=y_train.index,
        y=y_train.values,
        mode="lines",
        name="Train (actual)",
        line=dict(width=1)
    ))

    # Actual future values
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot["actual"],
        mode="lines",
        name="Actual future",
        line=dict(width=1, dash="dot")
    ))

    # Forecast
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot["forecast"],
        mode="lines",
        name="Forecast",
        line=dict(width=2)
    ))

    # Confidence interval band
    fig.add_trace(go.Scatter(
        x=list(df_plot.index) + list(df_plot.index[::-1]),
        y=list(df_plot["upper"]) + list(df_plot["lower"][::-1]),
        fill="toself",
        fillcolor="rgba(100,149,237,0.25)",
        line=dict(color="rgba(255,255,255,0)"),
        hoverinfo="skip",
        showlegend=True,
        name="95% CI"
    ))

    fig.update_layout(
        title=f"{target} forecast in {selected_area}",
        xaxis_title="Time",
        yaxis_title="kWh",
        legend=dict(orientation="h", y=-0.2),
        margin=dict(t=50, b=50)
    )

    st.plotly_chart(fig, use_container_width=True)


    # =====================================================
    # OPTIONAL: ERROR METRICS (MAE, RMSE)
    # =====================================================
    if not y_future_actual.isna().all():
        errors = y_future_actual - mean_forecast
        mae = np.mean(np.abs(errors))
        rmse = float(np.sqrt(np.mean(errors**2)))

        st.markdown(
            f"**MAE (future window)**: {mae:,.2f}  |  "
            f"**RMSE (future window)**: {rmse:,.2f}"
        )

else:
    st.caption("Adjust the settings and click **Run SARIMAX Forecast** to train the model.")
