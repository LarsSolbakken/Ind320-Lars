import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


# =========================================================
# PAGE TITLE
# =========================================================
st.title("📈 Plot")


# =========================================================
# OPTIONAL: CSV LOADING FUNCTION (kept for completeness)
# =========================================================
@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """
    Load and preprocess a local CSV file.
    
    Caching ensures:
    - File is only read once per session
    - Speedy reloads during reruns
    
    Pipeline:
      1) Read CSV.
      2) Check for required 'time' column.
      3) Convert 'time' strings → datetime.
      4) Drop invalid timestamps.
      5) Set time as index and sort chronologically.
    """
    df = pd.read_csv(path)

    # Ensure the column exists before processing further
    if "time" not in df.columns:
        st.error("Expected a 'time' column in the CSV.")
        st.stop()  # Stop page execution safely

    # Parse datetime; invalid entries become NaT
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Cleanup: drop NaT rows, set index, sort
    df = df.dropna(subset=["time"]).set_index("time").sort_index()

    return df


# =========================================================
# LOAD DATA FROM SESSION STATE
# =========================================================
# Weather data should be loaded previously on the Table page
df = st.session_state.get("df_weather")
if df is None:
    st.warning("Please select a city and year on the Table page first.")
    st.stop()  # Cannot proceed without data


# =========================================================
# METADATA DISPLAY (City + Year)
# =========================================================
city = st.session_state.get("selected_city", "Unknown city")
year = st.session_state.get("selected_year", "Unknown year")

st.markdown(f"### 🌍 Showing data for **{city} ({year})**")
st.caption("Data fetched from the Open-Meteo API and stored in session state.")


# =========================================================
# 1) IDENTIFY NUMERIC COLUMNS FOR PLOTTING
# =========================================================
# Only numeric values (float/int) can be meaningfully plotted
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

if not numeric_cols:
    st.warning("No numeric columns found.")
    st.stop()


# =========================================================
# 2) RESTORE PREVIOUS USER SETTINGS (for good UX)
# =========================================================
default_months = st.session_state.get("plot_months")
default_choice = st.session_state.get("plot_choice", "All columns")
default_exclude = st.session_state.get("plot_exclude", True)
default_norm = st.session_state.get("plot_normalize", True)


# =========================================================
# 3) TIME RANGE SELECTION (by months)
# =========================================================
# Convert the timestamp index to monthly periods (2021-03, etc.)
months = pd.Index(df.index.to_period("M")).unique().sort_values()

# Restore previously selected range if available and still valid
if default_months and all(m in months for m in default_months):
    start, end = default_months
else:
    start, end = months[0], months[0]  # Default to first month only

# Range slider for selecting month interval
start, end = st.select_slider(
    "Select month range",
    options=months,
    value=(start, end),
    format_func=lambda p: p.strftime("%Y-%m"),
)


# =========================================================
# 4) COLUMN SELECTION + OPTIONS (Normalize, Exclude wind direction)
# =========================================================
# Dropdown to choose one specific variable or all
choice = st.selectbox(
    "Column",
    ["All columns"] + numeric_cols,
    index=(["All columns"] + numeric_cols).index(default_choice)
)

# Exclude wind direction columns (optional)
exclude_dir = st.checkbox("Exclude wind direction (°)", value=default_exclude)

# Normalize all columns using z-score (optional)
normalize = st.checkbox("Normalize when plotting all columns (z-score)", value=default_norm)


# Save UI selections so state persists when switching pages
st.session_state["plot_months"] = (start, end)
st.session_state["plot_choice"] = choice
st.session_state["plot_exclude"] = exclude_dir
st.session_state["plot_normalize"] = normalize


# =========================================================
# 5) FILTER DATA TO SELECTED MONTH WINDOW
# =========================================================
# Convert timestamps → months and filter between selected range
mask = (df.index.to_period("M") >= start) & (df.index.to_period("M") <= end)

# Keep only numeric columns (wind, temp, direction, speed, etc.)
d = df.loc[mask, numeric_cols].copy()


# =========================================================
# 6) BUILD PLOTLY FIGURE (Multi-line or single line)
# =========================================================
if choice == "All columns":
    # Work on a copy so we don’t modify original filtered DataFrame
    d_plot = d.copy()

    # Optionally drop wind direction columns (0–360° ranges distort plots)
    if exclude_dir:
        drop_cols = [c for c in d_plot.columns if "direction" in c.lower()]
        d_plot = d_plot.drop(columns=drop_cols, errors="ignore")

    # Optionally normalize each variable (z-score) to compare scale
    if normalize:
        d_plot = (d_plot - d_plot.mean()) / d_plot.std(ddof=0)
        ylab = "z-score"
    else:
        ylab = "value"

    # Convert to long-form so Plotly Express can create multi-line interactive chart
    df_melted = d_plot.reset_index().melt(
        id_vars="time",
        var_name="Variable",
        value_name=ylab
    )

    fig = px.line(
        df_melted,
        x="time",
        y=ylab,
        color="Variable",
        title="Imported data (interactive)",
        labels={"time": "Date"},
    )

else:
    # Plot only the selected column
    fig = px.line(
        d.reset_index(),
        x="time",
        y=choice,
        title=choice,
        labels={"time": "Date", choice: choice},
    )


# =========================================================
# 7) FINAL LAYOUT TWEAKS
# =========================================================
fig.update_layout(
    template="plotly_white",
    legend=dict(
        orientation="h",
        yanchor="bottom", y=-0.3,
        xanchor="center", x=0.5
    ),
    margin=dict(t=50, b=50, l=50, r=50)
)


# =========================================================
# 8) RENDER PLOT
# =========================================================
st.plotly_chart(fig, use_container_width=True)
