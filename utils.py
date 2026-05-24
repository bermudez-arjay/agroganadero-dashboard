# utils.py
import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    # Tu lógica actual de conexión
    db_url = st.secrets["db_credentials"]["connection_string"]
    conn = psycopg2.connect(db_url)
    # ... cargar tus DataFrames ...
    return sales, credits, batches, customers, products