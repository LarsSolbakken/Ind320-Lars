import streamlit as st
import pandas as pd
import plotly.express as px

# Load consumption dataset from MongoDB (custom function you implemented)
from utils.db import load_consumption_data


# =========================================================
# PAGE SETTINGS
# =========================================================
st.set_page_config(page_title="⚡ Electricity Consumption in Norway", layout="wide")
st.title("⚡ Electricity Consumption in Norway (Elhub 2021–2024)")


# =========================================================
# LOAD AND STORE ENERGY DATA
# =========================================================

# Load all consumption data from MongoDB into a DataFrame
df = load_consumption_data()

# Store consumption data in session_state so other pages (correlation, SARIMAX, etc.)
# can access it without loading from the DB again.
st.session_state["consumption_data"] = df

# Find which years exist in the dataset for display purposes
years = sorted(df["starttime"].dt.year.unique())
st.caption(f"Available years in database: {', '.join(map(str, years))}")


# =========================================================
# UI DESCRIPTION
# =========================================================
# Explain to the user what is being shown
st.write("Visualizing electricity **consumption** data from Elhub API, stored in MongoDB.")


# =========================================================
# COLOR MAP (consumption groups)
# =========================================================
# Fixed colors for each consumption group
colors = {
    "household": "#0080FF",
    "industry": "#FF5733",
    "services": "#28B463",
    "other": "#7f7f7f"
}

# Human-friendly labels for price areas
price_area_names = {
    "NO1": "NO1 (Østlandet)",
    "NO2": "NO2 (Sørlandet)",
    "NO3": "NO3 (Midt-Norge)",
    "NO4": "NO4 (Nord-Norge)",
    "NO5": "NO5 (Vestlandet)"
}


# =========================================================
# GLOBAL FILTERS
# =========================================================
st.subheader("Filters")

# Extract available price areas from the dataset
price_areas = sorted(df["pricearea"].unique())

# Let user choose a price area via radio buttons with descriptive labels
selected_label = st.radio(
    "Select Price Area",
    [price_area_names[p] for p in price_areas],
    horizontal=True
)

# Convert label back to actual area code
selected_area = [k for k, v in price_area_names.items() if v == selected_label][0]

# Save selected area in session_state so other pages pick it up automatically
st.session_state["selected_area"] = selected_area

# Map price area → representative city (used by weather pages)
area2city = {
    "NO1": "Oslo",
    "NO2": "Kristiansand",
    "NO3": "Trondheim",
    "NO4": "Tromsø",
    "NO5": "Bergen"
}

# Save selected city to session_state so weather pages can use it
st.session_state["selected_city"] = area2city[selected_area]


# =========================================================
# TIME RANGE SELECTION (MONTHS)
# =========================================================

# Determine min/max timestamps in the dataset
min_date = df["starttime"].min()
max_date = df["starttime"].max()

# Monthly start dates for the slider (MS = month start)
months = pd.date_range(min_date, max_date, freq="MS")

# Dual slider for selecting a month–month range
start, end = st.select_slider(
    "Select time range",
    options=months,
    value=(months[0], months[-1]),
    format_func=lambda p: p.strftime("%b %Y")
)


# =========================================================
# PAGE LAYOUT
# =========================================================
# Two-column layout for pie chart and line chart
col1, col2 = st.columns(2)


# =========================================================
# LEFT COLUMN — PIE CHART
# =========================================================
with col1:
    st.subheader("Total Consumption by Group")

    # Filter dataset to selected area + selected date range
    df_area = df[
        (df["pricearea"] == selected_area) &
        (df["starttime"] >= start) &
        (df["starttime"] <= end)
    ]

    # Sum consumption per group over the chosen period
    totals = df_area.groupby("consumptiongroup")["quantitykwh"].sum()

    # Show total (converted from kWh → GWh)
    st.metric("Total Consumption (GWh)", f"{totals.sum()/1e6:.1f}")

    # Create pie chart showing proportion by consumption group
    fig1 = px.pie(
        values=totals.values,
        names=totals.index,
        color=totals.index,
        color_discrete_map=colors,
        title=f"Total Consumption in {selected_area}"
    )

    st.plotly_chart(fig1, use_container_width=True)


# =========================================================
# RIGHT COLUMN — LINE CHART
# =========================================================
with col2:
    st.subheader("Consumption Trends")

    # All consumption groups (ensure "other" is listed last)
    cons_groups = sorted(df["consumptiongroup"].unique())
    if "other" in cons_groups:
        cons_groups = [g for g in cons_groups if g != "other"] + ["other"]

    # Multi-selector for which groups to show in the line plot
    selected_groups = st.pills(
        "Select Consumption Groups",
        cons_groups,
        default=cons_groups,
        selection_mode="multi"
    )

    # Filter data for selected groups and date range
    df_range = df[
        (df["pricearea"] == selected_area) &
        (df["consumptiongroup"].isin(selected_groups)) &
        (df["starttime"] >= start) &
        (df["starttime"] <= end)
    ]

    if df_range.empty:
        # If filters produce no data, show a warning
        st.warning("No data available for this selection.")
    else:
        # Line chart of hourly consumption for selected groups
        fig2 = px.line(
            df_range,
            x="starttime",
            y="quantitykwh",
            color="consumptiongroup",
            color_discrete_map=colors,
            title=f"Consumption in {selected_area}, {start.strftime('%b %Y')} – {end.strftime('%b %Y')}"
        )

        fig2.update_layout(
            xaxis_title="Date",
            yaxis_title="kWh",
            legend_title="Consumption Group"
        )

        st.plotly_chart(fig2, use_container_width=True)

        # =====================================================
        # SUMMARY TABLE
        # =====================================================

        # Compute total GWh per group for this filtered range
        summary = df_range.groupby("consumptiongroup")["quantitykwh"].sum().reset_index()
        summary["Consumption (GWh)"] = (summary["quantitykwh"]/1e6).round(2)
        summary = summary.drop(columns=["quantitykwh"])

        # Keep "other" at the bottom if present
        if "other" in summary["consumptiongroup"].values:
            other_row = summary[summary["consumptiongroup"] == "other"]
            summary = summary[summary["consumptiongroup"] != "other"].sort_values(
                by="Consumption (GWh)", ascending=False
            )
            summary = pd.concat([summary, other_row])
        else:
            summary = summary.sort_values(by="Consumption (GWh)", ascending=False)

        st.write("### Summary for selected range")
        st.dataframe(summary.reset_index(drop=True))


# =========================================================
# DATA SOURCE
# =========================================================
with st.expander("ℹ️ Data Source"):
    st.markdown("""
    Data retrieved from the **Elhub API**, processed with **Spark**,  
    stored in **MongoDB Atlas**, and visualized using Streamlit.
    """)
