📘 README — IND320 Project
Weather–Energy Analytics Dashboard (Norway 2021–2024)
📌 Overview
This project is developed as part of IND320 – Data-Driven Energy Analytics.
The goal is to build an integrated platform that combines:
Elhub hourly electricity production and consumption data (2021–2024) stored in MongoDB Atlas
ERA5 Open-Meteo weather data (temperature, precipitation, wind)
Interactive analytics and machine learning models using Streamlit
The result is a full application that supports analysis of Norwegian price areas (NO1–NO5) and visualizes how weather, energy production, and anomalies interact across time and geography.
🚀 Features (Streamlit Application)
0. Map & Area Analysis
Interactive Folium map with NO1–NO5 GeoJSON overlays
Click any coordinate to select a point
Selected price area is highlighted
Used as the global area selector for all other pages
1. Electricity Production
Load data from MongoDB (production + consumption)
Pie chart of production mix
Time-series line plot per group
Summary table (GWh) for the chosen month range
2.1 Tables
Show weather data (ERA5) for the selected city (Oslo, Bergen, etc.)
Sparkline charts for each variable
First-month trends table
Stored in session state for use across pages
2.2 Plot Overview
Interactive multi-line time-series viewer for weather data
Supports:
month selection
include/exclude wind direction
normalization (z-score)
“all columns” or single-variable mode
2.3 STL & Spectrogram
STL decomposition (trend, seasonality, residual)
Spectrogram analysis of hourly signals
Works per (area, production group)
2.4 Outliers & Anomalies
Temperature outlier detection using DCT + SPC
Precipitation anomaly detection using LOF (Local Outlier Factor)
Interactive parameter tuning (cutoff, std multiplier, contamination)
3.1 Meteorology ↔ Production Correlation
Merge weather + production data
Compute sliding-window correlations
Adjustable:
lag (±48h)
window (6–336h)
3.2 Forecasting (SARIMAX)
Build a configurable SARIMAX model
Supports exogenous regressors:
other energy groups
optional weather variables
Forecast horizon: up to 168 hours
Confidence intervals + error metrics (MAE, RMSE)
3.3 Snow Drift & Wind Rose
Multi-year ERA5 weather download
Compute seasonal snow transport using Tabler (2003)
Directional wind-sector snow drift
Estimate effective fence height
🗃 Data Sources
Energy
Elhub Electricity Data API (hourly production & consumption)
Stored in MongoDB Atlas
Fetched using the custom function load_elhub_data()
Meteorology
ERA5 reanalysis via Open-Meteo Archive API
Used for:
temperature
precipitation
wind speed & direction
snow drift calculations
🛠 Tech Stack
Python 3.12
Streamlit (UI)
MongoDB Atlas (database)
Pandas / NumPy (data manipulation)
Plotly (interactive visualizations)
Folium (maps)
Statsmodels (SARIMAX)
Scikit-learn (LOF anomalies)
SciPy (DCT, spectrogram)
Shapely (geospatial click detection)
📦 Installation
Clone the repository:
git clone https://github.com/LarsSolbakken/Ind320-Lars.git
cd Ind320-Lars
Create + activate your environment:
conda create -n ind320 python=3.12
conda activate ind320
Install dependencies:
pip install -r requirements.txt
Add your MongoDB URI in:
.streamlit/secrets.toml
Then run the app:
streamlit run streamlit_app.py
📁 Project Structure
Ind320-Lars/
│
├── streamlit_app.py
├── requirements.txt
├── utils/
├── pages/
│   ├── 0. Map & Area Analysis.py
│   ├── 1. Electricity Production.py
│   ├── 2.1 Tables.py
│   ├── 2.2 Plot Overview.py
│   ├── 2.3 STL & Spectrogram.py
│   ├── 2.4 Outliers & Anomalies.py
│   ├── 3.1 Meteorology ↔ Production Correlation.py
│   ├── 3.2 Forecasting (SARIMAX).py
│   ├── 3.3 Snow Drift.py
│
├── data/
├── notebooks/
│   ├── part1
│   ├── part2
│   ├── part3
│   ├── part4
│
└── .streamlit/
    └── secrets.toml
🎯 Learning Outcomes
Process, transform, and store energy data using MongoDB
Integrate weather data (ERA5) for analytics
Build an end-to-end Streamlit dashboard
Apply advanced methods:
STL decomposition
Spectrogram analysis
DCT outlier detection
LOF anomaly detection
Sliding-window correlation
SARIMAX forecasting
Tabler snow drift model
✒️ Author
Lars Solbakken
IND320 — Data-Driven Energy Analytics
Norwegian University of Life Sciences (NMBU)