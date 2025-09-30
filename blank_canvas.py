import streamlit as st
button=st.button("start")
if button:
    st.write("Ready")

import random
@st.cache_data
def random():
    random_number = random.randint(1, 100)

if button:
    
