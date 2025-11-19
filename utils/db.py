from pymongo import MongoClient
from pymongo.server_api import ServerApi
import streamlit as st
import pandas as pd


# =========================================================
# MONGODB CLIENT (cached as resource)
# =========================================================
@st.cache_resource
def get_mongo_client():
    """
    Create and cache a MongoDB client using the connection URI
    stored in Streamlit's secrets.

    Why cache_resource?
    -------------------
    - Ensures we only create ONE MongoClient during an entire app session.
    - Prevents reconnections on every rerun.
    - Faster & avoids unnecessary load on the MongoDB server.
    """
    uri = st.secrets["mongo"]["uri"]     # Provided via .streamlit/secrets.toml
    return MongoClient(uri, server_api=ServerApi("1"))



# =========================================================
# LOAD FULL ELHUB DATA (Production + Consumption)
# =========================================================
@st.cache_data
def load_elhub_data():
    """
    Load *both* production and consumption time-series from MongoDB.

    Returns
    -------
    (df_prod, df_cons) : tuple of DataFrames
        df_prod : production_per_group_hour
        df_cons : consumption_per_group_hour

    This function:
        - Connects to the 'elhub2021' database
        - Queries both collections (production + consumption)
        - Converts them to pandas DataFrames
        - Parses 'starttime' into datetime

    Cached with @st.cache_data so repeated loads are instant.
    """
    client = get_mongo_client()
    db = client["elhub2021"]

    # Query both collections, excluding MongoDB's default _id field
    prod_docs = list(db["production_per_group_hour"].find({}, {"_id": 0}))
    cons_docs = list(db["consumption_per_group_hour"].find({}, {"_id": 0}))

    df_prod = pd.DataFrame(prod_docs)
    df_cons = pd.DataFrame(cons_docs)

    # Ensure consistent datetime format
    df_prod["starttime"] = pd.to_datetime(df_prod["starttime"], errors="coerce")
    df_cons["starttime"] = pd.to_datetime(df_cons["starttime"], errors="coerce")

    return df_prod, df_cons



# =========================================================
# PRODUCTION-ONLY LOADER (wrapper)
# =========================================================
@st.cache_data
def load_production_data():
    """
    Convenience wrapper that returns ONLY production data.

    Why separate?
    -------------
    Many pages in the Streamlit app visualize production only.
    This avoids unpacking unnecessarily every time.
    """
    df_prod, _ = load_elhub_data()
    return df_prod



# =========================================================
# CONSUMPTION-ONLY LOADER (wrapper)
# =========================================================
@st.cache_data
def load_consumption_data():
    """
    Convenience wrapper that returns ONLY consumption data.
    """
    _, df_cons = load_elhub_data()
    return df_cons
