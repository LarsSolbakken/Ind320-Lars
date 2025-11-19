import numpy as np
import pandas as pd
from scipy.fftpack import dct, idct
from sklearn.neighbors import LocalOutlierFactor
from statsmodels.tsa.seasonal import STL
from scipy.signal import spectrogram
import plotly.graph_objects as go


# =========================================================
# SPC + DCT OUTLIER DETECTION (Temperature)
# =========================================================
def detect_outliers(temp_series, cutoff=100, std_mult=2):
    """
    Detect temperature outliers using:
    1) DCT high-pass filtering for deseasonalization
    2) Statistical Process Control (SPC) bounds

    Parameters
    ----------
    temp_series : pandas.Series
        Time-indexed temperature series in °C.
    cutoff : int
        Number of low-frequency DCT coefficients to retain as seasonal baseline.
        Higher cutoff = less smoothing → fewer outliers detected.
    std_mult : float
        Standard deviation multiplier for SPC bounds (e.g. ±2σ).

    Returns
    -------
    fig : plotly.graph_objects.Figure
        Interactive plot showing raw temps, SPC bands, and detected outliers.
    summary : None
        (Kept for potential future return of metrics)
    outliers_df : pandas.Series
        Outlier values with timestamps.
    """
    values = temp_series.values

    # Discrete Cosine Transform: separate signal into frequency components
    dct_coeff = dct(values, norm="ortho")

    # High-frequency signal (residual variation)
    dct_coeff_high = dct_coeff.copy()
    dct_coeff_high[:cutoff] = 0
    satv = idct(dct_coeff_high, norm="ortho")

    # Low-frequency seasonal baseline
    dct_coeff_low = dct_coeff.copy()
    dct_coeff_low[cutoff:] = 0
    seasonal = idct(dct_coeff_low, norm="ortho")

    # SPC control limits following seasonal baseline
    mean = np.mean(satv)
    std = np.std(satv)
    upper = seasonal + (mean + std_mult * std)
    lower = seasonal + (mean - std_mult * std)

    # Detect when observed temperature exceeds limits
    mask_outliers = (values > upper) | (values < lower)
    outliers_df = temp_series[mask_outliers]

    # Plotly interactive visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=temp_series.index, y=values,
                             mode="lines", name="Temperature"))
    fig.add_trace(go.Scatter(x=outliers_df.index, y=outliers_df.values,
                             mode="markers", name="Outliers", marker=dict(color="red")))
    fig.add_trace(go.Scatter(x=temp_series.index, y=upper,
                             mode="lines", name=f"+{std_mult}σ", line=dict(dash="dash")))
    fig.add_trace(go.Scatter(x=temp_series.index, y=lower,
                             mode="lines", name=f"-{std_mult}σ", line=dict(dash="dash")))

    fig.update_layout(
        title="Temperature Outlier Detection (Seasonal SPC + DCT)",
        yaxis_title="Temperature (°C)",
        height=600,
    )
    return fig, None, outliers_df



# =========================================================
# LOF ANOMALY DETECTION (Precipitation)
# =========================================================
def detect_anomalies(series, n_neighbors=20, proportion=0.005):
    """
    Detect anomalies in precipitation using Local Outlier Factor (LOF).

    Parameters
    ----------
    series : pandas.Series
        Time-indexed precipitation signal in mm.
    n_neighbors : int
        Controls local density comparison scale.
    proportion : float
        Expected fraction of anomalies (contamination rate).

    Returns
    -------
    fig : plotly Figure
        Scatter plot marking anomaly points.
    summary : None
        Placeholder for future reporting.
    anomalies_df : pandas.Series
        Anomalous data points with timestamps.
    """
    values = series.values.reshape(-1, 1)

    lof = LocalOutlierFactor(n_neighbors=n_neighbors, contamination=proportion)
    preds = lof.fit_predict(values)

    anomalies_df = series[preds == -1]  # LOF labels -1 as anomaly

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values,
        mode="markers", name="Precipitation",
    ))
    fig.add_trace(go.Scatter(
        x=anomalies_df.index, y=anomalies_df.values,
        mode="markers", name="Anomalies", marker=dict(color="red"),
    ))

    fig.update_layout(
        title="Precipitation Anomaly Detection (LOF)",
        yaxis_title="Precipitation (mm)",
        height=600,
    )
    return fig, None, anomalies_df



# =========================================================
# STL DECOMPOSITION (Energy data)
# =========================================================
def stl_decompose(data, area, group, period=24, seasonal=13, trend=91, robust=True):
    """
    Seasonal-Trend decomposition using LOESS (STL).
    Designed for hourly electricity production from Elhub.

    Parameters
    ----------
    data : DataFrame
        Must contain: pricearea, productiongroup, starttime, quantitykwh
    area : str (e.g., "NO1")
    group : str (e.g., "hydro")
    period : int
        Hours per seasonal cycle (24 = daily seasonality)
    seasonal : int
        Seasonal smoothing window
    trend : int
        Trend smoothing window
    robust : bool
        Robust to outliers

    Returns
    -------
    fig : plotly Figure showing trend, seasonal and residual components
    """
    df = data[(data["pricearea"] == area) & (data["productiongroup"] == group)].copy()
    df["starttime"] = pd.to_datetime(df["starttime"])
    df = df.set_index("starttime").sort_index()

    stl = STL(df["quantitykwh"], period=period,
              seasonal=seasonal, trend=trend, robust=robust)
    res = stl.fit()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=res.trend, name="Trend"))
    fig.add_trace(go.Scatter(x=df.index, y=res.seasonal, name="Seasonal"))
    fig.add_trace(go.Scatter(x=df.index, y=res.resid, name="Residual"))

    fig.update_layout(
        title=f"STL Decomposition – {group} in {area}",
        xaxis_title="Time",
        yaxis_title="kWh",
        height=600,
    )
    return fig



# =========================================================
# SPECTROGRAM (Energy frequency analysis)
# =========================================================
def make_spectrogram(data, area, group, window_length=168, overlap=84):
    """
    Inspect frequency content of electricity production signals.

    Parameters
    ----------
    data : DataFrame
        Must contain hourly production data for different groups.
    area : str
        Price area (NO1–NO5).
    group : str
        Production group (hydro, wind, …).
    window_length : int
        FFT window size in hours (168h = 1 week).
    overlap : int
        Overlap between adjacent windows.

    Returns
    -------
    fig : plotly Heatmap
        Frequency vs time power spectrum in dB scale.
    """
    df = data[(data["pricearea"] == area) & (data["productiongroup"] == group)].copy()
    df["starttime"] = pd.to_datetime(df["starttime"])
    df = df.set_index("starttime").sort_index()

    signal = df["quantitykwh"].values
    fs = 1  # 1 sample per hour

    # Compute spectrogram
    f, t, Sxx = spectrogram(signal, fs=fs, nperseg=window_length, noverlap=overlap)

    # Convert power to decibels for better contrast
    Sxx_dB = 10 * np.log10(Sxx + 1e-12)

    fig = go.Figure(data=go.Heatmap(
        x=t,
        y=f,
        z=Sxx_dB,
        colorbar=dict(title="Power (dB)"),
    ))
    fig.update_layout(
        title=f"Spectrogram – {group} in {area}",
        xaxis_title="Time (hours)",
        yaxis_title="Frequency (cycles/hour)",
        height=600,
    )
    return fig
