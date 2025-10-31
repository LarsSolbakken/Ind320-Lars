import requests   # 👈 add this line
import pandas as pd
def download_weather(lon, lat, year):
    """
    Download historical weather data (ERA5 reanalysis) for a given location and year.
    
    Parameters:
        lon (float): Longitude of the location
        lat (float): Latitude of the location
        year (int): Year (e.g. 2019)
    
    Returns:
        pd.DataFrame: Weather time series
    """
    # Open-Meteo ERA5 API endpoint
    url = "https://archive-api.open-meteo.com/v1/era5"
    
    # Parameters (you can add more variables if needed)
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": f"{year}-01-01",
        "end_date": f"{year}-12-31",
        "hourly": ["temperature_2m", "precipitation"],
        "timezone": "Europe/Oslo"
    }
    
    # Send request
    response = requests.get(url, params=params)
    response.raise_for_status()  # error handling
    
    data = response.json()
    
    # Convert to DataFrame
    df = pd.DataFrame({
        "time": data["hourly"]["time"],
        "temperature_2m": data["hourly"]["temperature_2m"],
        "precipitation": data["hourly"]["precipitation"]
    })
    
    # Convert time to datetime
    df["time"] = pd.to_datetime(df["time"])
    # Set time as index and sort for easier time-series analysis
    df = df.set_index("time").sort_index()
    return df


import numpy as np
import matplotlib.pyplot as plt
from scipy.fftpack import dct, idct

def detect_outliers(temp_series, cutoff=100, std_mult=2):
    """
    Detect temperature outliers using DCT high-pass filter + SPC.
    
    Parameters:
        temp_series (pd.Series): Time-indexed temperature series
        cutoff (int): Frequency cutoff for DCT filtering (lower = smoother seasonal component removed)
        std_mult (float): Number of std deviations for SPC boundaries
    
    Returns:
        fig, ax, outliers_df
    """
    # --- Step 1: Apply DCT ---
    values = temp_series.values
    dct_coeff = dct(values, norm="ortho")  # transform
    
    # Zero out low-frequency terms (keep only seasonal-adjusted variations)
    dct_coeff[:cutoff] = 0
    satv = idct(dct_coeff, norm="ortho")
    
    # --- Step 2: SPC boundaries ---
    mean = np.mean(satv)
    std = np.std(satv)
    upper = mean + std_mult * std
    lower = mean - std_mult * std
    
    # Outliers = where SATV is outside bounds
    mask_outliers = (satv > upper) | (satv < lower)
    outliers_df = temp_series[mask_outliers]
    
    # --- Step 3: Plot ---
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(temp_series.index, temp_series.values, label="Temperature", alpha=0.7)
    ax.scatter(outliers_df.index, outliers_df.values, color="red", label="Outliers")
    ax.axhline(upper, color="green", linestyle="--", label=f"+{std_mult}σ")
    ax.axhline(lower, color="green", linestyle="--", label=f"-{std_mult}σ")
    ax.set_title("Temperature Outlier Detection (SPC + DCT)")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    
    return fig, ax, outliers_df


from sklearn.neighbors import LocalOutlierFactor

def detect_anomalies(series, proportion=0.005):
    """
    Detect precipitation anomalies using Local Outlier Factor (LOF).
    
    Parameters:
        series (pd.Series): Time-indexed precipitation series
        proportion (float): Expected proportion of anomalies
    
    Returns:
        fig, ax, anomalies_df
    """
    values = series.values.reshape(-1, 1)
    
    lof = LocalOutlierFactor(n_neighbors=20, contamination=proportion)
    preds = lof.fit_predict(values)  # -1 = anomaly, 1 = normal
    
    mask_anomalies = preds == -1
    anomalies_df = series[mask_anomalies]
    
    # --- Plot ---
    fig, ax = plt.subplots(figsize=(12,6))
    ax.plot(series.index, series.values, label="Precipitation", alpha=0.7)
    ax.scatter(anomalies_df.index, anomalies_df.values, color="red", label="Anomalies")
    ax.set_title("Precipitation Anomaly Detection (LOF)")
    ax.set_ylabel("Precipitation (mm)")
    ax.legend()
    
    return fig, ax, anomalies_df



from statsmodels.tsa.seasonal import STL
import matplotlib.pyplot as plt

def stl_decompose(data, area, group, period=24, seasonal=13, trend=91, robust=True):
    """
    Perform STL decomposition on Elhub production data.

    Parameters:
        data (pd.DataFrame): Must contain columns [startTime, priceArea, productionGroup, quantityKWh]
        area (str): Price area code, e.g. 'NO1'
        group (str): Production group, e.g. 'hydro'
        period (int): Seasonal period length (e.g. 24 for daily seasonality in hourly data)
        seasonal (int): Seasonal smoother
        trend (int): Trend smoother
        robust (bool): Robust to outliers

    Returns:
        fig: Matplotlib figure with decomposition plots
        res: STL result object (with trend, seasonal, resid)
    """
    # Filter for chosen area and group
    df = data[(data["pricearea"] == area) & (data["productiongroup"] == group)].copy()

    # Use startTime as index
    df["starttime"] = pd.to_datetime(df["starttime"])
    df = df.set_index("starttime").sort_index()

    # Run STL on the quantity column
    stl = STL(df["quantitykwh"], period=period, seasonal=seasonal, trend=trend, robust=robust)
    res = stl.fit()

    # Plot decomposition
    fig = res.plot()
    fig.set_size_inches(12, 8)
    plt.suptitle(f"STL Decomposition – {group} in {area}", fontsize=14)

    return fig, res



from scipy.signal import spectrogram
import matplotlib.pyplot as plt
import numpy as np

def make_spectrogram(data, area, group, window_length=168, overlap=84):
    """
    Create a spectrogram for Elhub production data.

    Parameters:
        data (pd.DataFrame): Must contain columns [startTime, priceArea, productionGroup, quantityKWh]
        area (str): Price area code, e.g. 'NO1'
        group (str): Production group, e.g. 'hydro'
        window_length (int): Window length in samples (e.g. 168 for 1 week of hourly data)
        overlap (int): Number of samples to overlap between windows (e.g. 84 for 50%)
    
    Returns:
        fig, ax: Matplotlib figure and axis with the spectrogram plot
    """
    # --- 1. Filter data ---
    df = data[(data["pricearea"] == area) & (data["productiongroup"] == group)].copy()
    df["starttime"] = pd.to_datetime(df["starttime"])
    df = df.set_index("starttime").sort_index()

    signal = df["quantitykwh"].values
    fs = 1  # 1 sample per hour

    # --- 2. Compute spectrogram ---
    f, t, Sxx = spectrogram(signal, fs=fs, nperseg=window_length, noverlap=overlap)
    
    # --- 3. Plot ---
    fig, ax = plt.subplots(figsize=(12, 6))
    pcm = ax.pcolormesh(t, f, 10 * np.log10(Sxx + 1e-12), shading='auto', cmap='viridis')
    fig.colorbar(pcm, ax=ax, label="Power (dB)")
    
    ax.set_title(f"Spectrogram – {group} in {area}")
    ax.set_xlabel("Time (days)")
    ax.set_ylabel("Frequency (cycles/hour)")
    
    return fig, ax
