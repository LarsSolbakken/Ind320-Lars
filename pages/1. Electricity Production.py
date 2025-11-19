import streamlit as st 
st.title("⚡ Electricity Production in Norway (Elhub 2021-2024)")


import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
from utils.db import load_production_data





# Load all production data from MongoDB (wrapped in utils/db)
df = load_production_data()

# Store the full DataFrame in Streamlit's session state so it can be
# re-used across multiple pages without reloading from MongoDB.
st.session_state["elhub_data"] = df

# Extract which calendar years are present in the dataset.
# This is shown to users as metadata about data coverage.
years = sorted(df["starttime"].dt.year.unique())

# Display available years under the title as a small caption.
st.caption(f"Available years in database: {', '.join(map(str, years))}")



# -------------------------
# Streamlit UI setup
# -------------------------

st.write("Visualizing electricity production data from Elhub API, stored in MongoDB.")

# Define consistent colors for each production group
colors = {
    "hydro": "#1f77b4",
    "wind": "#2ca02c",
    "solar": "#ffbb00",
    "thermal": "#d62728",
    "other": "#7f7f7f"
}

# Map price area codes (NO1–NO5) to region names for easier interpretation
price_area_names = {
    "NO1": "NO1 (Østlandet)",
    "NO2": "NO2 (Sørlandet)",
    "NO3": "NO3 (Midt-Norge)",
    "NO4": "NO4 (Nord-Norge)",
    "NO5": "NO5 (Vestlandet)"
}

# -------------------------
# Global filters (shared by both plots)
# -------------------------
st.subheader("Filters")


# --- Create radio buttons for selecting price area ---
# price_areas contains codes like ['NO1', 'NO2', ...]
price_areas = sorted(df["pricearea"].unique())

# Display area names (e.g. “NO1 – Oslo”) instead of codes
selected_label = st.radio(
    "Select Price Area",
    [price_area_names[p] for p in price_areas],
    horizontal=True
)

# Convert selected label back to area code (e.g. “NO1”)
selected_area = [k for k, v in price_area_names.items() if v == selected_label][0]

# Store selection in Streamlit session state for global access
st.session_state["selected_area"] = selected_area

# --- Map area → representative city for weather data ---
area2city = {"NO1": "Oslo", "NO2": "Kristiansand", "NO3": "Trondheim", "NO4": "Tromsø", "NO5": "Bergen"}

# Save the matching city name in session state for other pages (e.g. Table & Plot)
st.session_state["selected_city"] = area2city[selected_area]



#  Month range slider (choose start and end month)

min_date = df["starttime"].min()
max_date = df["starttime"].max()

# Create month labels dynamically
months = pd.date_range(min_date, max_date, freq="MS")

# Year–month slider
start, end = st.select_slider(
    "Select time range",
    options=months,
    value=(months[0], months[-1]),
    format_func=lambda p: p.strftime("%b %Y")
)


# Split page into two columns (pie chart left, line plot right)
col1, col2 = st.columns(2)

# ---- Left Column: Pie Chart ----
with col1:
    st.subheader("Total Production by Group")
   
   
    df_area = df[
    (df["pricearea"] == selected_area) &
    (df["starttime"] >= start) &
    (df["starttime"] <= end)
    ]


    # Aggregate total production per group
    totals = df_area.groupby("productiongroup")["quantitykwh"].sum()

    # Display total production in GWh as a metric above the chart
    st.metric("Total Production (GWh)", f"{totals.sum()/1e6:.1f}")

    # Pie chart showing share of each production group


    fig1 = px.pie(
        values=totals.values,
        names=totals.index,
        color=totals.index,
        color_discrete_map=colors,
        title=f"Total Production in {selected_area}"
)

    st.plotly_chart(fig1, use_container_width=True)


# ---- Right Column: Line Plot ----
with col2:
    st.subheader("Monthly Production Trends")

    # Ensure "other" group is always shown last in the pill selector
    prod_groups = sorted(df["productiongroup"].unique())
    if "other" in prod_groups:
        prod_groups = [g for g in prod_groups if g != "other"] + ["other"]

    # Pills allow multiple group selection
    selected_groups = st.pills(
        "Select Production Groups",
        prod_groups,
        default=prod_groups,
        selection_mode="multi"
    )
    
    # Filter dataset by selected area, production groups, and time range
    df_range = df[
        (df["pricearea"] == selected_area) &
        (df["productiongroup"].isin(selected_groups)) &
        (df["starttime"] >= start) &
        (df["starttime"] <= end)
    ]
   
    # If no data available for the selection, show warning
    if df_range.empty:
        st.warning("No data available for this selection.")
    else:
        # Line plot of hourly production, grouped by production group
        fig2 = px.line(
            df_range,
            x="starttime",
            y="quantitykwh",
            color="productiongroup",
            color_discrete_map=colors,
            title=f"Production in {selected_area}, {start.strftime('%b %Y')} – {end.strftime('%b %Y')}"
        )

        fig2.update_layout(
            # height=350,
            # margin=dict(l=10, r=10, t=40, b=10),
            xaxis_title="Date",
            yaxis_title="kWh",
            legend_title="Production Group"
        )

        st.plotly_chart(fig2, use_container_width=True)


        # Table: total production per group in GWh
        summary = df_range.groupby("productiongroup")["quantitykwh"].sum().reset_index()
        summary["Production (GWh)"] = (summary["quantitykwh"]/1e6).round(2)  # convert to GWh
        summary = summary.drop(columns=["quantitykwh"])  # drop raw column

        # Sort by Production (descending), but keep "other" last
        if "other" in summary["productiongroup"].values:
            other_row = summary[summary["productiongroup"] == "other"]
            summary = summary[summary["productiongroup"] != "other"] \
                .sort_values(by="Production (GWh)", ascending=False)
            summary = pd.concat([summary, other_row])
        else:
            summary = summary.sort_values(by="Production (GWh)", ascending=False)

        # Reset index to avoid showing 0,1,2,3
        summary = summary.reset_index(drop=True)

        st.write("### Summary for selected range")
        st.dataframe(summary)

# ---- Expander with source info ----
with st.expander("ℹ️ Data Source"):
    st.markdown("""
    Data retrieved from the [Elhub API](https://api.elhub.no/energy-data/v0/price-areas),
    processed with Spark + Cassandra, and stored in MongoDB Atlas for visualization.
    """)
