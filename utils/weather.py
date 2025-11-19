import requests
import pandas as pd
import streamlit as st


# =========================================================
# BASIC ERA5 WEATHER (Temp + Precip)
# =========================================================
def download_weather(lon, lat, year):
    """
    Download ERA5 hourly weather data for one full year.
    Minimal version used by the Table/Plot pages.

    Parameters
    ----------
    lon : float
        Longitude of location.
    lat : float
        Latitude of location.
    year : int
        Calendar year to download (Jan 1 – Dec 31).

    Returns
    -------
    DataFrame
        Indexed by datetime, containing:
        - temperature_2m (°C)
        - precipitation (mm)
    """
    url = "https://archive-api.open-meteo.com/v1/era5"

    # Request temperature & precipitation only
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "hourly": ["temperature_2m", "precipitation"],
        "timezone": "Europe/Oslo",
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    # Build consistent DataFrame
    df = pd.DataFrame({
        "time": data["hourly"]["time"],
        "temperature_2m": data["hourly"]["temperature_2m"],
        "precipitation": data["hourly"]["precipitation"],
    })

    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time").sort_index()



# =========================================================
# EXTENDED ERA5 WEATHER (Temp + Precip + Wind)
# =========================================================
@st.cache_data
def download_weather2(lon, lat, year):
    """
    Full ERA5 weather: temperature, precipitation, wind speed & direction.
    This version is used in:
      - Snow drift model
      - Correlation page
      - SARIMAX (bonus exogenous variables)

    Parameters
    ----------
    lon, lat : float
        Geographic coordinate.
    year : int
        Calendar year to download.

    Returns
    -------
    DataFrame
        Indexed by datetime, with columns:
        - temperature_2m (°C)
        - precipitation (mm)
        - wind_speed_10m (m/s)
        - wind_direction_10m (°)
    """
    url = "https://archive-api.open-meteo.com/v1/era5"

    # Expanded list of meteorological variables
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "hourly": [
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
            "wind_direction_10m",
        ],
        "timezone": "Europe/Oslo",
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()

    # Build DataFrame with clear, unit-annotated column names
    df = pd.DataFrame({
        "time": data["hourly"]["time"],
        "temperature_2m (°C)": data["hourly"]["temperature_2m"],
        "precipitation (mm)": data["hourly"]["precipitation"],
        "wind_speed_10m (m/s)": data["hourly"]["wind_speed_10m"],
        "wind_direction_10m (°)": data["hourly"]["wind_direction_10m"],
    })

    df["time"] = pd.to_datetime(df["time"])
    return df.set_index("time").sort_index()



# =========================================================
# MULTI-YEAR WEATHER + SEASON LABELING (Snow Drift Page)
# =========================================================
@st.cache_data
def load_weather_range(lat, lon, start_year, end_year):
    """
    Download multiple years of ERA5 weather and assign season labels.
    Used specifically for the Snow Drift & Wind Rose page.

    A "season" is defined as:
        July 1 – June 30
    so July–December belong to the same season as January–June next year.

    Parameters
    ----------
    lat, lon : float
        Geographic coordinate.
    start_year : int
        First calendar year to include.
    end_year : int
        Final year to include (inclusive).

    Returns
    -------
    DataFrame
        With columns for:
        - all weather variables
        - 'season' (int)
        - 'time' (DatetimeIndex duplicated as column)
    """
    # Import here to avoid circular import
    from .weather import download_weather2

    dfs = []

    # Download each year independently
    for y in range(start_year, end_year + 1):
        df_y = download_weather2(lon, lat, y)

        # Compute season:
        #   - If month >= July → season = current year
        #   - If month < July  → season = previous year
        df_y["season"] = df_y.index.year.where(
            df_y.index.month >= 7,
            df_y.index.year - 1,
        )

        dfs.append(df_y)

    # Combine all years
    df_weather = pd.concat(dfs)

    # Add explicit 'time' column (useful for merging operations later)
    df_weather["time"] = df_weather.index

    return df_weather
