import streamlit as st
# from utils import stl_decompose, make_spectrogram   # old import path
from utils.plots import stl_decompose, make_spectrogram
import matplotlib.pyplot as plt
import plotly.graph_objects as go


# =========================================================
# PAGE TITLE
# =========================================================
st.title("📊 STL & Spectrogram Analysis")


# =========================================================
# LOAD ELHUB DATA FROM SESSION STATE
# =========================================================
# The Electricity Production page stores the full MongoDB dataset in:
#   st.session_state["elhub_data"]
# This ensures all analysis pages can access the same data without reloading.
elhub_data = st.session_state.get("elhub_data")

if elhub_data is None:
    # User has not visited the production page yet, so we cannot continue.
    st.warning("No Elhub data found. Visit the Electricity Production page first.")
    st.stop()


# =========================================================
# CREATE ANALYSIS TABS
# =========================================================
# Users can switch between:
#   - STL decomposition (trend/seasonality)
#   - Spectrogram (frequency representation)
tab1, tab2 = st.tabs(["STL decomposition", "Spectrogram"])


# =========================================================
# TAB 1 — STL DECOMPOSITION
# =========================================================
with tab1:
    st.subheader("STL decomposition of Elhub data")

    # Determine selected price area from session state ("NO1"–"NO5")
    # This is chosen on the Production page.
    area = st.session_state.get("selected_area", "NO1")

    # Dropdown for selecting which production group to analyze
    # Only hydro and wind implemented in utilities.
    group = st.selectbox("Production group", ["hydro", "wind"])

    # Perform the STL decomposition (Trend + Seasonal + Residual)
    # stl_decompose() returns a ready-to-display Plotly figure.
    fig = stl_decompose(elhub_data, area, group)

    # Render the interactive decomposition plot
    st.plotly_chart(fig, use_container_width=True)



# =========================================================
# TAB 2 — SPECTROGRAM ANALYSIS
# =========================================================
with tab2:
    st.subheader("Spectrogram of production data")

    # Use selected area from session state again
    area = st.session_state.get("selected_area", "NO1")

    # Allow user to select production group (hydro or wind)
    # Must use a different key than previous selectbox to avoid Streamlit conflicts.
    group = st.selectbox("Production group", ["hydro", "wind"], key="spectro_group")

    # Generate spectrogram via utility function
    # Spectrogram visualizes energy over frequency components across time.
    fig = make_spectrogram(elhub_data, area, group)

    # Display interactive spectrogram
    st.plotly_chart(fig, use_container_width=True)
