import streamlit as st
from utils import stl_decompose, make_spectrogram
import matplotlib.pyplot as plt

# --- Page title ---
st.title("📊 STL & Spectrogram Analysis")

# --- Retrieve Elhub production data from session state ---
# This data should have been loaded earlier on the Electricity Production page.
elhub_data = st.session_state.get("elhub_data")
if elhub_data is None:
    # Stop rendering if no Elhub data available
    st.warning("No Elhub data found. Visit the Electricity Production page first.")
    st.stop()

# --- Create two analysis tabs ---
tab1, tab2 = st.tabs(["STL decomposition", "Spectrogram"])

# --- Tab 1: STL Decomposition ---
with tab1:
    st.subheader("STL decomposition of Elhub data")

    # Get selected area (e.g. NO1–NO5) and choose production group
    area = st.session_state.get("selected_area", "NO1")
    group = st.selectbox("Production group", ["hydro", "wind"])

    # Perform Seasonal-Trend decomposition using LOESS
    fig, _ = stl_decompose(elhub_data, area, group)

    # Display resulting plot
    st.pyplot(fig)

# --- Tab 2: Spectrogram Analysis ---
with tab2:
    st.subheader("Spectrogram of production data")

    # Again, use selected area and allow group selection (with a unique key)
    area = st.session_state.get("selected_area", "NO1")
    group = st.selectbox("Production group", ["hydro", "wind"], key="spectro_group")

    # Generate and display spectrogram for production signal
    fig, _ = make_spectrogram(elhub_data, area, group)
    st.pyplot(fig)
