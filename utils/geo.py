import json
import streamlit as st
import pandas as pd
from shapely.geometry import Point


def load_geojson(path: str = "data/file.geojson"):
    """
    Load a GeoJSON file from disk.

    Parameters
    ----------
    path : str
        File path to the GeoJSON (default: "data/file.geojson").

    Returns
    -------
    dict
        Parsed GeoJSON structure with "type", "features", etc.

    Notes
    -----
    This is used by the map page to:
    - draw price area polygons (NO1–NO5)
    - detect which polygon (price area) a user clicked in Folium
    """
    with open(path) as f:
        return json.load(f)


@st.cache_data
def build_id_to_name(gj):
    """
    Build a mapping from GeoJSON feature ID → price area name.

    Parameters
    ----------
    gj : dict
        Loaded GeoJSON structure containing "features", each of which
        has an "id" and properties including "ElSpotOmr".

    Returns
    -------
    dict
        Example:
        {
            "1": "NO 1",
            "2": "NO 2",
            ...
        }

    Notes
    -----
    - The Folium map uses this mapping to color polygons correctly.
    - The map page also uses this to display area names when the user clicks.
    - Cached with st.cache_data because GeoJSON does not change often.
    """
    out = {}
    for f in gj["features"]:
        fid = str(f["id"])                      # ensure IDs become string keys
        name = f["properties"]["ElSpotOmr"]     # canonical price area name (e.g., "NO 3")
        out[fid] = name
    return out
