import streamlit as st
import pandas as pd
from pathlib import Path
import numpy as np
# from utils import download_weather   # old import, replaced by updated module
from utils.weather import download_weather


# =========================================================
# PAGE TITLE
# =========================================================
# Displayed at the top of the Streamlit page
st.title('📊 Table')


# =========================================================
# OPTIONAL: LOAD LOCAL CSV (NOT USED IN THIS PAGE ANYMORE)
# =========================================================
# This function remains for reference and reproducibility if
# you ever switch back to using a bundled CSV instead of API.
@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    """
    Load and preprocess a local CSV file.

    Caching ensures:
      - The file is only read once per session
      - The page reloads instantly on re-rerun

    Steps:
      1. Read CSV into pandas.
      2. Ensure a 'time' column exists.
      3. Convert the 'time' column to proper datetime.
      4. Drop rows with invalid timestamps.
      5. Index by 'time' and ensure chronological sorting.
    """
    df = pd.read_csv(path)

    # Safety check: required column must be present
    if "time" not in df.columns:
        st.error("Expected a 'time' column in the CSV.")
        st.stop()

    # Convert 'time' strings → datetime objects; invalid as NaT
    df["time"] = pd.to_datetime(df["time"], errors="coerce")

    # Remove invalid rows, index by 'time', and sort chronologically
    df = df.dropna(subset=["time"]).set_index("time").sort_index()

    return df


# =========================================================
# CITY → COORDINATES MAPPING
# =========================================================
# Used to fetch weather from Open-Meteo based on the selected city.
city_coordinates = {
    "Oslo": {"lon": 10.75, "lat": 59.91},
    "Kristiansand": {"lon": 8.00, "lat": 58.15},
    "Trondheim": {"lon": 10.40, "lat": 63.43},
    "Tromsø": {"lon": 18.96, "lat": 69.65},
    "Bergen": {"lon": 5.32, "lat": 60.39}
}


# =========================================================
# RESTORE PREVIOUS SESSION SELECTIONS
# =========================================================
# The app remembers the last chosen city and year so that users can
# navigate between pages without resetting their selections.
default_city = st.session_state.get("selected_city", "Oslo")
default_year = st.session_state.get("selected_year", 2021)


# =========================================================
# USER INPUTS
# =========================================================
# City selection dropdown — defaults to previous selection
city = st.selectbox(
    "Select city",
    list(city_coordinates.keys()),
    index=list(city_coordinates.keys()).index(default_city)
)

# Year selector — shows integer input from 2019–2024
year = st.number_input("Year", 2019, 2024, default_year)


# Coordinates used for weather lookup
coords = city_coordinates[city]


# =========================================================
# FETCH WEATHER DATA FROM OPEN-METEO
# =========================================================
# download_weather() is a utility from utils/weather which:
#   - Calls the Open-Meteo API
#   - Returns a cleaned pandas DataFrame
#   - Ensures 'time' is datetime and used as index
df = download_weather(coords["lon"], coords["lat"], year)


# =========================================================
# UPDATE SESSION STATE
# =========================================================
# Keep user choices and loaded weather data for other pages
st.session_state["selected_city"] = city
st.session_state["selected_year"] = year
st.session_state["df_weather"] = df


# =========================================================
# IDENTIFY NUMERIC COLUMNS FOR SUMMARY TABLE
# =========================================================
# LineChartColumn only works with numeric data, so we pull
# all integer/float columns from the weather DataFrame.
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()


# =========================================================
# FILTER TO FIRST MONTH OF THE DATASET
# =========================================================
# df.index[0] → earliest timestamp
# to_period("M") converts it into a monthly period (e.g. "2024-02")
first_month = df.index[0].to_period("M")

# Keep only rows from that month
df_first = df[df.index.to_period("M") == first_month]


# =========================================================
# BUILD A TABLE FOR STREAMLIT'S LineChartColumn
# =========================================================
# We create one row per numeric variable.
# Each row contains:
#   - the variable name
#   - a list of that variable's values over the first month
#
# LineChartColumn will automatically render a tiny sparkline
# from the list stored in each cell of "first_month_series".
table = pd.DataFrame({
    "variable": numeric_cols,
    "first_month_series": [df_first[c].dropna().tolist() for c in numeric_cols],
})


# =========================================================
# DISPLAY THE TABLE WITH SPARKLINES
# =========================================================
# This produces a clean dynamic table where each row contains:
#  - The variable name
#  - A small inline line chart of that variable's monthly trend
st.dataframe(
    table,
    column_config={
        "variable": st.column_config.TextColumn("Variable"),
        "first_month_series": st.column_config.LineChartColumn("First month"),
    },
    use_container_width=True,  # Fill horizontal space
    hide_index=True,           # Cleaner appearance
)
