import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    db_url = st.secrets["db_credentials"]["connection_string"]
    with psycopg2.connect(db_url) as conn:
        # 1. Ventas con nombre de vendedor
        sales = pd.read_sql_query("""
            SELECT s.total_amount, s.created_at, a.first_name as vendor_name 
            FROM sales s JOIN admins a ON s.admin_id = a.id WHERE s.deleted_at IS NULL;
        """, conn)
        
        # 2. Créditos
        credits = pd.read_sql_query("SELECT total_amount, pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
        
        # 3. Lotes
        batches = pd.read_sql_query("SELECT code, current_quantity, state FROM batches WHERE deleted_at IS NULL;", conn)
        
        # 4. Clientes
        customers = pd.read_sql_query("SELECT id FROM customers WHERE deleted_at IS NULL;", conn)
        
        # 5. Productos
        products = pd.read_sql_query("SELECT id, name, selling_price FROM products WHERE deleted_at IS NULL;", conn)
        
        return sales, credits, batches, customers, products