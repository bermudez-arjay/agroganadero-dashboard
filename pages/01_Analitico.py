import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_production_data

st.set_page_config(page_title="Dashboard Analítico", layout="wide")

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

st.title("📊 Análisis Profundo de Operaciones")

# --- RESUMEN GENERAL (Sin filtros) ---
st.subheader("Resumen de Rendimiento Global")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"C${df_sales['total_amount'].sum():,.2f}")
col2.metric("Stock Global", f"{df_batches['current_quantity'].sum():,.0f}")
col3.metric("Cartera Pendiente", f"C${df_credits['pending_balance'].sum():,.2f}")
col4.metric("Clientes Activos", len(df_customers))

st.markdown("---")

# --- ANÁLISIS DE PRODUCTOS (Sección opcional) ---
st.subheader("Análisis Detallado por Insumo")
selected_product = st.selectbox("Seleccionar Insumo para ver detalle:", df_products['name'].unique())

prod_row = df_products[df_products['name'] == selected_product].iloc[0]
prod_batches = df_batches[df_batches['product_id'] == prod_row['id']]

if not prod_batches.empty:
    # Fila de métricas del producto
    sub_col1, sub_col2 = st.columns(2)
    sub_col1.metric("Stock del Producto", prod_batches['current_quantity'].sum())
    sub_col2.metric("Lotes Activos", len(prod_batches))

    # Visualizaciones con control de seguridad
    row2_c1, row2_c2 = st.columns(2)
    
    with row2_c1:
        st.write("Distribución de Cantidades")
        fig_bar = px.bar(prod_batches, x='code', y='current_quantity', template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    with row2_c2:
        st.write("Estado de Lotes")
        # Validamos que 'state' tenga valores antes de graficar
        if 'state' in prod_batches.columns and not prod_batches['state'].isna().all():
            fig_pie = px.pie(prod_batches, names='state', hole=0.5, template="plotly_dark")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No hay estados de lotes disponibles para este producto.")
else:
    st.warning("No hay lotes registrados para este insumo.")

# Tabla de detalle
st.subheader("Detalle de Registros")
st.dataframe(prod_batches, use_container_width=True)