import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

# Page title in the Streamlit app
st.title("📈 Plot")

# Path to the local CSV file shipped with the app
# CSV_PATH = Path("open-meteo-subset.csv")

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """
    Read the CSV once and cache the result for speed.
    - Parses 'time' to real datetimes.
    - Drops rows with invalid times.
    - Uses 'time' as the index (DatetimeIndex) and sorts chronologically.
    """
    df = pd.read_csv(path)
    # Safety: ensure the expected 'time' column exists
    if "time" not in df.columns:
        st.error("Expected a 'time' column in the CSV.")
        st.stop()  # stop rendering rather than crashing later
    # Parse 'time' strings -> datetime; bad values become NaT
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    # Remove rows with invalid/NaT time, set as index, sort by time
    df = df.dropna(subset=["time"]).set_index("time").sort_index()
    return df

# --- Load data (cached) ---
# df = load_data(CSV_PATH)
df = st.session_state.get("df_weather")
if df is None:
    st.warning("Please select a city and year on the Table page first.")
    st.stop()

# --- Display current dataset info ---
city = st.session_state.get("selected_city", "Unknown city")
year = st.session_state.get("selected_year", "Unknown year")

st.markdown(f"### 🌍 Showing data for **{city} ({year})**")
st.caption("Data fetched from the Open-Meteo API and stored in session state.")


# 2) Pick numeric columns we can plot (ints/floats)
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
if not numeric_cols:
    st.warning("No numeric columns found."); st.stop()

# # 3) UI controls
# # Derive the list of months present in the data (as Periods), sorted
# months = pd.Index(df.index.to_period("M")).unique().sort_values()

# # Range slider over months; default = first month only
# start, end = st.select_slider(
#     "Select month range",
#     options=months,
#     value=(months[0], months[0]),
#     format_func=lambda p: p.strftime("%Y-%m"),  # pretty label like 2024-01
# ) 

# # Dropdown to choose a single column or all columns
# choice = st.selectbox("Column", ["All columns"] + numeric_cols, index=0)

# # Optional helpers for nicer "all columns" plots
# exclude_dir = st.checkbox("Exclude wind direction (°)", value=True)
# normalize   = st.checkbox("Normalize when plotting all columns (z-score)", value=True)
# --- Remember last settings using st.session_state ---

# Get defaults from session if they exist, else use initial defaults
default_months = st.session_state.get("plot_months")
default_choice = st.session_state.get("plot_choice", "All columns")
default_exclude = st.session_state.get("plot_exclude", True)
default_norm = st.session_state.get("plot_normalize", True)

# Derive the list of months present in the data (as Periods), sorted
months = pd.Index(df.index.to_period("M")).unique().sort_values()

# If user has visited before, restore previous month selection
if default_months and all(m in months for m in default_months):
    start, end = default_months
else:
    start, end = months[0], months[0]

# Range slider with remembered values
start, end = st.select_slider(
    "Select month range",
    options=months,
    value=(start, end),
    format_func=lambda p: p.strftime("%Y-%m"),
)

# Dropdown to choose column (remembered)
choice = st.selectbox(
    "Column",
    ["All columns"] + numeric_cols,
    index=(["All columns"] + numeric_cols).index(default_choice)
)

# Checkboxes with remembered states
exclude_dir = st.checkbox("Exclude wind direction (°)", value=default_exclude)
normalize = st.checkbox("Normalize when plotting all columns (z-score)", value=default_norm)

# 🧠 Save all user choices in session_state
st.session_state["plot_months"] = (start, end)
st.session_state["plot_choice"] = choice
st.session_state["plot_exclude"] = exclude_dir
st.session_state["plot_normalize"] = normalize


# 4) Filter rows to the selected month window (mask is True for rows inside range)
mask = (df.index.to_period("M") >= start) & (df.index.to_period("M") <= end)
d = df.loc[mask, numeric_cols].copy()  # subset of rows + only numeric columns

# Optionally drop wind direction (angles 0–360° can dominate/mislead on shared axis)



# 5) Build the plot canvas
fig, ax = plt.subplots()

if choice == "All columns":
    if exclude_dir:
        for name in list(d.columns):
            # Intent: drop columns whose name contains 'direction' (and/or degree symbol)
            # NOTE: this condition is likely incorrect Python logic; see note below.
            if "direction" in name.lower():
                d.drop(columns=name, inplace=True, errors="ignore")
    # Normalize series to comparable scale if user asked (z-score)
    if normalize:
        d_plot = (d - d.mean()) / d.std(ddof=0)  # column-wise standardization
        ylab = "z-score"
    else:
        d_plot = d
        ylab = "value"

    # Plot each (possibly normalized) column on the same axes
    for col in d_plot.columns:
        ax.plot(d_plot.index, d_plot[col], label=col)

    ax.set_title("Imported data")
    ax.set_xlabel("Date")
    ax.set_ylabel(ylab)
    ax.legend(loc="upper left")

else:
    # Single column: plot raw values for the chosen column
    ax.plot(d.index, d[choice])
    ax.set_title(choice)
    ax.set_xlabel("Date")
    ax.set_ylabel(choice)

# Render the matplotlib figure inside Streamlit
st.pyplot(fig)
