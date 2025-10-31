import streamlit as st; 


st.set_page_config(page_title="Open-Meteo Explorer", layout="wide")
st.title('IND320 • Home')

st.sidebar.header("Navigation")
# Built-in page links (works in recent Streamlit versions)
# st.sidebar.page_link("streamlit_app.py", label="🏠 Home")
# st.sidebar.page_link("pages/1_Table.py", label="📊 Table")
# st.sidebar.page_link("pages/2_Plot.py", label="📈 Plot")
# st.sidebar.page_link("pages/Electricity_Production.py", label="⚡ Electricity Production Dashboard (Elhub 2021)")

st.sidebar.page_link("streamlit_app.py", label="🏠 Home")
st.sidebar.page_link("pages/1_Electricity_Production.py", label="⚡ Electricity Production Dashboard (Elhub 2021)")
st.sidebar.page_link("pages/2_STL_and_Spectrogram.py", label="📊 STL & Spectrogram")
st.sidebar.page_link("pages/3_Table.py", label="📊 Table")
st.sidebar.page_link("pages/4_Plot.py", label="📈 Plot")
st.sidebar.page_link("pages/5_Outliers_and_Anomalies.py", label="🔍 Outliers & Anomalies")