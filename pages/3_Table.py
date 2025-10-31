import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
from utils import download_weather

# Page title in the Streamlit app
st.title('📊 Table')

# Path to the local CSV file shipped with the app
# CSV_PATH = Path("open-meteo-subset.csv")

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """
    Read the CSV once and cache the result for speed.
    - Parses the 'time' column to real datetimes.
    - Drops rows with invalid times.
    - Uses 'time' as the index (DatetimeIndex), sorted chronologically.
    """
    df = pd.read_csv(path)

    # Safety check: this app expects a 'time' column
    if "time" not in df.columns:
        st.error("Expected a 'time' column in the CSV.")
        st.stop()  # stop rendering this page rather than crashing later

    # Convert 'time' from strings to datetime; invalid values become NaT
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Remove rows where time couldn't be parsed; set as index; sort by time
    df = df.dropna(subset=["time"]).set_index("time").sort_index()

    return df

city_coordinates = {
    "Oslo": {"lon": 10.75, "lat": 59.91},
    "Kristiansand": {"lon": 8.00, "lat": 58.15},
    "Trondheim": {"lon": 10.40, "lat": 63.43},
    "Tromsø": {"lon": 18.96, "lat": 69.65},
    "Bergen": {"lon": 5.32, "lat": 60.39}
}

# --- Restore previous selections if they exist ---
default_city = st.session_state.get("selected_city", "Oslo")
default_year = st.session_state.get("selected_year", 2019)

city = st.selectbox("Select city", list(city_coordinates.keys()), index=list(city_coordinates.keys()).index(default_city))
year = st.number_input("Year", 2019, 2024, default_year)

coords = city_coordinates[city]

# Fetch data from Open-Meteo
df = download_weather(coords["lon"], coords["lat"], year)

# ✅ Fix: make 'time' the index
df = df.set_index("time").sort_index()

# Save to session state
st.session_state["selected_city"] = city
st.session_state["selected_year"] = year
st.session_state["df_weather"] = df
# --- Load the dataset (cached) ---
# df = load_data(CSV_PATH)

# Identify which columns are numeric (ints/floats) — those are the variables we’ll summarize/plot
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

# Determine the first month present in the time index.
# df.index[0] is the earliest timestamp (because we sorted); to_period("M") converts it to a month period like 2024-01.
first_month = df.index[0].to_period("M")

# Filter the DataFrame to only rows that fall within that first month
df_first = df[df.index.to_period("M") == first_month]

# --- Build the per-variable table for LineChartColumn ---
# We make one row per numeric variable:
#  - 'variable': the column name
#  - 'first_month_series': a list of that column's values in the first month (LineChartColumn expects a list per cell)
table = pd.DataFrame({
    "variable": numeric_cols,
    "first_month_series": [df_first[c].dropna().tolist() for c in numeric_cols],
})

# Render the table in Streamlit.
# column_config tells Streamlit to:
#  - display 'variable' as plain text,
#  - render 'first_month_series' as a small line chart (sparkline) per row.
st.dataframe(
    table,
    column_config={
        "variable": st.column_config.TextColumn("Variable"),
        "first_month_series": st.column_config.LineChartColumn("First month"),
    },
    use_container_width=True,  # stretch to page width
    hide_index=True,           # cleaner look without row numbers
)
# st.experimental_rerun()