import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
from shapely.geometry import shape, Point

# Local utilities for GeoJSON loading, name mapping, and DB fetch
from utils.geo import load_geojson, build_id_to_name
from utils.db import load_elhub_data




# =========================================================
# 1. PAGE CONFIGURATION
# =========================================================
st.set_page_config(page_title="Price Area Map (NO1–NO5)", layout="wide")
st.title("🗺️ Price Areas – Interactive Map")


# =========================================================
# 2. LOAD GEOJSON FILE (Price area shapes from NVE)
# =========================================================
# load_geojson() returns a FeatureCollection with polygons for NO1–NO5.
geojson_data = load_geojson()

# Ensure polygon IDs are strings (folium requires consistent ID types)
for f in geojson_data["features"]:
    f["id"] = str(f["id"])

# Extract all polygon IDs
poly_ids = [f.get("id") for f in geojson_data["features"]]


# =========================================================
# 3. LOAD DATA FROM MONGODB (Production & Consumption)
# =========================================================
# load_elhub_data() returns two DataFrames:
# df_prod: all production hour-level records
# df_cons: all consumption hour-level records
df_prod, df_cons = load_elhub_data()


# =========================================================
# 4. BUILD MAPPING FROM FEATURE ID → HUMAN NAME (e.g. "NO 1")
# =========================================================
# Example: {"1": "NO 1", "2": "NO 2", ...}
id_to_name = build_id_to_name(geojson_data)


# =========================================================
# 5. PREPARE SHAPELY POLYGONS FOR POINT-IN-POLYGON TESTS
# =========================================================
# Used so we can detect which polygon a clicked point belongs to.
if "polygons" not in st.session_state:
    polys = []
    for feat in geojson_data["features"]:
        fid = feat.get("id")          # Feature ID
        geom = shape(feat["geometry"]) # Convert GeoJSON geometry → Shapely polygon
        polys.append((fid, geom))
    st.session_state.polygons = polys


# =========================================================
# 6. FUNCTION: Find which price area polygon contains a point
# =========================================================
def find_feature_id(lon, lat):
    """
    Given lon/lat coordinates, return the feature (polygon) ID
    of the price area the point belongs to. Returns None if outside.
    """
    pt = Point(lon, lat)
    for fid, geom in st.session_state.polygons:
        # covers() handles boundary conditions gracefully
        if geom.covers(pt):
            return fid
    return None


# =========================================================
# 7. INITIALIZE SESSION STATE (Pin location + selected area)
# =========================================================
# Default map center (mid-Norway)
if "last_pin" not in st.session_state:
    st.session_state.last_pin = [63.5, 15.0]

# Detect which price area this initial point belongs to
if "selected_feature_id" not in st.session_state:
    lat, lon = st.session_state.last_pin
    st.session_state.selected_feature_id = find_feature_id(lon, lat)


# =========================================================
# 8. USER FILTER CONTROLS (Sidebar-equivalent inside the page)
# =========================================================
st.subheader("Filters")

# User chooses "Production" or "Consumption"
data_type = st.radio("Data Type:", ["Production", "Consumption"], horizontal=True)

# Select which DataFrame & group column to use
if data_type == "Production":
    available_groups = sorted(df_prod["productiongroup"].unique())
    df = df_prod
    col_group = "productiongroup"
else:
    available_groups = sorted(df_cons["consumptiongroup"].unique())
    df = df_cons
    col_group = "consumptiongroup"

# Choose an energy group (e.g., "HYDRO RUN_OF_RIVER", "INDUSTRY", ...)
group = st.selectbox("Energy Group:", available_groups)

# Choose date interval from full dataset range
start_d = df["starttime"].min().date()
end_d  = df["starttime"].max().date()
start_date, end_date = st.date_input("Select date range:", [start_d, end_d])


# =========================================================
# 9. COMPUTE MEAN VALUES PER PRICE AREA (for colouring)
# =========================================================
# Filter by chosen group + date interval
filtered = df[
    (df[col_group] == group) &
    (df["starttime"] >= pd.to_datetime(start_date)) &
    (df["starttime"] <= pd.to_datetime(end_date))
]

# Compute mean kWh for each price area
means = filtered.groupby("pricearea")["quantitykwh"].mean().reset_index()

# Convert "NO1" → "NO 1" to match GeoJSON naming convention
means["ElSpotOmr"] = means["pricearea"].str.replace(r"NO(\d)", r"NO \1", regex=True)

# Map: Feature ID → mean value (used later for info panel)
value_map = {}
for fid, area_name in id_to_name.items():
    if area_name in means["ElSpotOmr"].values:
        value_map[fid] = means.loc[means["ElSpotOmr"] == area_name, "quantitykwh"].values[0]

# Missing areas get default value (shown as None)
DEFAULT_VALUE = None
for fid in id_to_name.keys():
    if fid not in value_map:
        value_map[fid] = DEFAULT_VALUE

# DataFrame structured for possible choropleth use (not used here)
df_vals = pd.DataFrame({
    "id": [str(k) for k in value_map.keys()],
    "value": list(value_map.values())
})


# =========================================================
# 10. LAYOUT (Map left, Info right)
# =========================================================
map_col, info_col = st.columns([2.2, 1])


# =========================================================
# 11. BUILD THE FOLIUM MAP
# =========================================================
with map_col:

    # Create the map centered at the last clicked point
    m = folium.Map(
        location=st.session_state.last_pin,
        zoom_start=5,
        tiles="OpenStreetMap"
    )

    # -----------------------------------------------------
    # FIXED-COLOUR PRICE AREA OVERLAYS (not choropleth)
    # -----------------------------------------------------
    # Instead of shading by mean value, the assignment is kept as-is
    # using predefined colors for each area.
    AREA_COLORS = {
        "NO 1": "blue",
        "NO 2": "green",
        "NO 3": "orange",
        "NO 4": "purple",
        "NO 5": "red",
    }

    def fixed_style(feature):
        """
        Choose a static color for each price area polygon.
        fillOpacity is set so overlapping layers remain visible.
        """
        area_name = feature["properties"]["ElSpotOmr"]
        color = AREA_COLORS.get(area_name, "gray")  # fallback color
        return {
            "fillColor": color,
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.5,
        }

    # Add all price area polygons with fixed colors
    folium.GeoJson(
        geojson_data,
        style_function=fixed_style,
        highlight_function=lambda f: {"weight": 3, "color": "yellow"},
    ).add_to(m)

    # -----------------------------------------------------
    # Highlight the selected polygon (red outline)
    # -----------------------------------------------------
    sel = st.session_state.selected_feature_id
    if sel is not None:
        sel_feats = [f for f in geojson_data["features"] if f.get("id") == sel]
        folium.GeoJson(
            {"type": "FeatureCollection", "features": sel_feats},
            style_function=lambda f: {"fillOpacity": 0, "color": "red", "weight": 3},
        ).add_to(m)

    # -----------------------------------------------------
    # Add pin marker at clicked coordinate
    # -----------------------------------------------------
    folium.Marker(
        location=st.session_state.last_pin,
        icon=folium.Icon(color="red"),
        popup=f"{st.session_state.last_pin[0]:.5f}, {st.session_state.last_pin[1]:.5f}"
    ).add_to(m)

    # -----------------------------------------------------
    # Render map + read click events from user
    # -----------------------------------------------------
    out = st_folium(m, height=650, width=None)

    # Update pin location + detect selected polygon on click
    if out and out.get("last_clicked"):
        lat = out["last_clicked"]["lat"]
        lon = out["last_clicked"]["lng"]
        new = [lat, lon]
        # Update the point only if user clicks somewhere new
        if new != st.session_state.last_pin:
            st.session_state.last_pin = new
            st.session_state.selected_feature_id = find_feature_id(lon, lat)
            st.rerun()


# =========================================================
# 12. RIGHT INFO PANEL (Metadata for selection)
# =========================================================
with info_col:
    st.subheader("Selection Info")

    # Show coordinate info
    lat, lon = st.session_state.last_pin
    st.write(f"Lat: {lat:.5f}")
    st.write(f"Lon: {lon:.5f}")

    # Show selected area + computed value
    sel = st.session_state.selected_feature_id
    if sel is None:
        st.write("Area: Outside price areas")
    else:
        st.write(f"Area: {id_to_name.get(sel, 'Unknown')}")
        st.write(f"Value: {value_map.get(sel, 0):,.2f} kWh")
