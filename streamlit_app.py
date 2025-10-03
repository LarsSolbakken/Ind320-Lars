import streamlit as st; 
st.title('IND320 • Home')

st.set_page_config(page_title="Open-Meteo Explorer", layout="wide")

st.sidebar.header("Navigation")
# Built-in page links (works in recent Streamlit versions)
st.sidebar.page_link("streamlit_app.py", label="🏠 Home")
st.sidebar.page_link("pages/1_Table.py", label="📊 Table")
st.sidebar.page_link("pages/2_Plot.py", label="📈 Plot")
st.sidebar.page_link("pages/3_Log_and_AI.py", label="📝 Log & AI notes")

