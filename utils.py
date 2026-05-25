import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    db_url = st.secrets["db_credentials"]["connection_string"]
    with psycopg2.connect(db_url) as conn:
        # Ventas totales y por vendedor para gráficos de barras
        sales = pd.read_sql_query("""
            SELECT s.total_amount, a.first_name as vendor_name 
            FROM sales s JOIN admins a ON s.admin_id = a.id WHERE s.deleted_at IS NULL;
        """, conn)
        
        # Créditos para métricas de riesgo
        credits = pd.read_sql_query("SELECT pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
        
        # Lotes para análisis de stock (distribución)
        batches = pd.read_sql_query("SELECT current_quantity, state FROM batches WHERE deleted_at IS NULL;", conn)
        
        # Productos para el detalle final
        products = pd.read_sql_query("SELECT name, selling_price FROM products WHERE deleted_at IS NULL;", conn)
        
        return sales, credits, batches, products