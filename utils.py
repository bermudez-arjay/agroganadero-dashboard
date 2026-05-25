import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    db_url = st.secrets["db_credentials"]["connection_string"]
    with psycopg2.connect(db_url) as conn:
        # Ventas
        sales = pd.read_sql_query("""
            SELECT s.total_amount, a.first_name as vendor_name, s.created_at 
            FROM sales s JOIN admins a ON s.admin_id = a.id WHERE s.deleted_at IS NULL;
        """, conn)
        
        # Compras
        purchases = pd.read_sql_query("""
            SELECT p.total_amount, s.company_name as supplier_name, p.purchase_date 
            FROM purchases p JOIN suppliers s ON p.supplier_id = s.id WHERE p.deleted_at IS NULL;
        """, conn)
        
        # Créditos y Lotes
        credits = pd.read_sql_query("SELECT pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
        batches = pd.read_sql_query("SELECT current_quantity, state FROM batches WHERE deleted_at IS NULL;", conn)
        products = pd.read_sql_query("SELECT name, selling_price FROM products WHERE deleted_at IS NULL;", conn)
        
        return sales, purchases, credits, batches, products