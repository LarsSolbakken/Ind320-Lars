import streamlit as st 
st.title("⚡ Electricity Production in Norway (Elhub 2021-2024)")

import pandas as pd
import plotly.express as px

# Load the cleaned production dataset stored in MongoDB
# (implemented in utils/db -> load_production_data)
from utils.db import load_production_data



# =========================================================
# LOAD AND STORE ENERGY DATA
# =========================================================

# Load all production data from MongoDB (cached inside load_production_data)
df = load_production_data()

# Save full dataset into session_state so other pages
# (weather correlation, SARIMAX, STL, anomaly detection, etc.)
# can access it WITHOUT reloading MongoDB again.
st.session_state["elhub_data"] = df

# Determine which calendar years exist in the dataset.
# Useful for giving users context about data availability.
years = sorted(df["starttime"].dt.year.unique())

# Display year coverage directly under the title.
st.caption(f"Available years in database: {', '.join(map(str, years))}")



# =========================================================
# UI DESCRIPTION
# =========================================================
st.write("Visualizing electricity production data from Elhub API, stored in MongoDB.")



# =========================================================
# COLOR MAPS & LOOKUP TABLES
# =========================================================

# Fixed color palette for production groups (stable across app)
colors = {
    "hydro": "#1f77b4",
    "wind": "#2ca02c",
    "solar": "#ffbb00",
    "thermal": "#d62728",
    "other": "#7f7f7f"
}

# More descriptive labels for price areas
price_area_names = {
    "NO1": "NO1 (Østlandet)",
    "NO2": "NO2 (Sørlandet)",
    "NO3": "NO3 (Midt-Norge)",
    "NO4": "NO4 (Nord-Norge)",
    "NO5": "NO5 (Vestlandet)"
}



# =========================================================
# GLOBAL FILTERS (Shared by pie chart + line plot)
# =========================================================
st.subheader("Filters")

# Extract unique price areas (strings like ['NO1', 'NO2', ...])
price_areas = sorted(df["pricearea"].unique())

# Let user pick an area using descriptive labels
selected_label = st.radio(
    "Select Price Area",
    [price_area_names[p] for p in price_areas],
    horizontal=True
)

# Convert the chosen descriptive name back to its area code (e.g. "NO1")
selected_area = [k for k, v in price_area_names.items() if v == selected_label][0]

# Save selected area globally — used by other pages (STL, SARIMAX, anomalies, etc.)
st.session_state["selected_area"] = selected_area

# Representative city per price area — used for weather data on other pages
area2city = {
    "NO1": "Oslo", 
    "NO2": "Kristiansand", 
    "NO3": "Trondheim", 
    "NO4": "Tromsø", 
    "NO5": "Bergen"
}

# Save selected city to session state so all weather-related pages can reuse it
st.session_state["selected_city"] = area2city[selected_area]



# =========================================================
# TIME RANGE SELECTION (Month-based)
# =========================================================

min_date = df["starttime"].min()
max_date = df["starttime"].max()

# Create a list of first-of-the-month timestamps for slider
months = pd.date_range(min_date, max_date, freq="MS")

# Dual-slider allowing user to pick a month–to–month range
start, end = st.select_slider(
    "Select time range",
    options=months,
    value=(months[0], months[-1]),
    format_func=lambda p: p.strftime("%b %Y")
)



# =========================================================
# PAGE LAYOUT (2 columns)
# =========================================================
col1, col2 = st.columns(2)



# =========================================================
# LEFT COLUMN — PIE CHART (TOTAL PRODUCTION)
# =========================================================
with col1:
    st.subheader("Total Production by Group")
   
    # Filter full dataset to chosen area + time range
    df_area = df[
        (df["pricearea"] == selected_area) &
        (df["starttime"] >= start) &
        (df["starttime"] <= end)
    ]

    # Sum total production per group (hydro/wind/etc.)
    totals = df_area.groupby("productiongroup")["quantitykwh"].sum()

    # Display aggregate (converted to GWh)
    st.metric("Total Production (GWh)", f"{totals.sum()/1e6:.1f}")

    # Pie chart showing proportional contribution of each production group
    fig1 = px.pie(
        values=totals.values,
        names=totals.index,
        color=totals.index,
        color_discrete_map=colors,
        title=f"Total Production in {selected_area}"
    )

    st.plotly_chart(fig1, use_container_width=True)



# =========================================================
# RIGHT COLUMN — LINE PLOT (TRENDS)
# =========================================================
with col2:
    st.subheader("Monthly Production Trends")

    # Sort groups so that "other" always appears last
    prod_groups = sorted(df["productiongroup"].unique())
    if "other" in prod_groups:
        prod_groups = [g for g in prod_groups if g != "other"] + ["other"]

    # Pill-style selector allows multiple groups simultaneously
    selected_groups = st.pills(
        "Select Production Groups",
        prod_groups,
        default=prod_groups,
        selection_mode="multi"
    )
    
    # Filter for trend plot
    df_range = df[
        (df["pricearea"] == selected_area) &
        (df["productiongroup"].isin(selected_groups)) &
        (df["starttime"] >= start) &
        (df["starttime"] <= end)
    ]
   
    # If selection gives no data, warn user
    if df_range.empty:
        st.warning("No data available for this selection.")
    else:
        # Line plot of hourly production for selected groups
        fig2 = px.line(
            df_range,
            x="starttime",
            y="quantitykwh",
            color="productiongroup",
            color_discrete_map=colors,
            title=f"Production in {selected_area}, {start.strftime('%b %Y')} – {end.strftime('%b %Y')}"
        )

        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="kWh",
            legend_title="Production Group"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # =====================================================
        # SUMMARY TABLE (per production group)
        # =====================================================

        # Total GWh per group
        summary = df_range.groupby("productiongroup")["quantitykwh"].sum().reset_index()
        summary["Production (GWh)"] = (summary["quantitykwh"]/1e6).round(2)
        summary = summary.drop(columns=["quantitykwh"])

        # Sort descending but keep "other" at bottom
        if "other" in summary["productiongroup"].values:
            other_row = summary[summary["productiongroup"] == "other"]
            summary = summary[summary["productiongroup"] != "other"].sort_values(
                by="Production (GWh)", ascending=False
            )
            summary = pd.concat([summary, other_row])
        else:
            summary = summary.sort_values(by="Production (GWh)", ascending=False)

        summary = summary.reset_index(drop=True)

        st.write("### Summary for selected range")
        st.dataframe(summary)



# =========================================================
# DATA SOURCE (EXPANDER)
# =========================================================
with st.expander("ℹ️ Data Source"):
    st.markdown("""
    Data retrieved from the **Elhub API**, processed using **Spark & Cassandra**,  
    and stored in **MongoDB Atlas** before visualization.
    """)
