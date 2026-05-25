import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    db_url = st.secrets["db_credentials"]["connection_string"]
    with psycopg2.connect(db_url) as conn:
        sales = pd.read_sql_query("SELECT total_amount, created_at FROM sales WHERE deleted_at IS NULL;", conn)
        credits = pd.read_sql_query("SELECT total_amount, pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
        batches = pd.read_sql_query("SELECT code, current_quantity, expiration_date, product_id FROM batches WHERE deleted_at IS NULL;", conn)
        customers = pd.read_sql_query("SELECT id FROM customers WHERE deleted_at IS NULL;", conn)
        # Importante: añadimos selling_price para el analítico
        products = pd.read_sql_query("SELECT id, name, selling_price FROM products WHERE deleted_at IS NULL;", conn)
        
    return sales, credits, batches, customers, products