import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    db_url = st.secrets["db_credentials"]["connection_string"]
    with psycopg2.connect(db_url) as conn:
        # Ventas
        sales = pd.read_sql_query("""
            SELECT s.total_amount, a.first_name as vendor_name 
            FROM sales s JOIN admins a ON s.admin_id = a.id WHERE s.deleted_at IS NULL;
        """, conn)
        # Créditos
        credits = pd.read_sql_query("SELECT pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
        # Lotes
        batches = pd.read_sql_query("SELECT current_quantity, state FROM batches WHERE deleted_at IS NULL;", conn)
        # Clientes
        customers = pd.read_sql_query("SELECT id FROM customers WHERE deleted_at IS NULL;", conn)
        # Productos
        products = pd.read_sql_query("SELECT name, selling_price FROM products WHERE deleted_at IS NULL;", conn)
        
        return sales, credits, batches, customers, products