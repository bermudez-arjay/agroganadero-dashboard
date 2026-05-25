import streamlit as st
import psycopg2
import pandas as pd

@st.cache_data(ttl=60)
def fetch_production_data():
    db_url = st.secrets["db_credentials"]["connection_string"]
    with psycopg2.connect(db_url) as conn:
        # Traemos datos detallados de ventas y sus responsables
        query_sales = """
        SELECT s.total_amount, s.created_at, a.first_name as vendor_name 
        FROM sales s 
        JOIN admins a ON s.admin_id = a.id 
        WHERE s.deleted_at IS NULL;
        """
        sales = pd.read_sql_query(query_sales, conn)
        
        # Traemos créditos para el análisis de cartera
        credits = pd.read_sql_query("SELECT total_amount, pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
        
        # Traemos detalles de ventas para el embudo (simulado por categorias o estados)
        # Aquí ajusta según cómo manejes las etapas en tu DB
        sale_details = pd.read_sql_query("SELECT sale_id, quantity, unit_selling_price FROM sale_details WHERE deleted_at IS NULL;", conn)
        
        return sales, credits, sale_details