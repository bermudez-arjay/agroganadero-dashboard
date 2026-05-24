import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_production_data  # Asegúrate de tener la conexión en utils.py

st.set_page_config(page_title="Dashboard Analítico", layout="wide")

st.markdown("## 📊 Análisis Profundo de Operaciones")

# Carga de datos
_, _, df_batches, _, df_products = fetch_production_data()

# --- FILTROS ---
st.sidebar.header("Filtros de Análisis")
selected_product = st.sidebar.selectbox("Seleccionar Insumo:", df_products['name'].unique())

# --- FILA 1: KPIs DE PRODUCTO ---
col1, col2, col3 = st.columns(3)

# Lógica de filtrado
prod_id = df_products[df_products['name'] == selected_product]['id'].values[0]
prod_batches = df_batches[df_batches['product_id'] == prod_id]
total_stock = prod_batches['current_quantity'].sum()

col1.metric("Stock Actual", f"{total_stock} Unidades")
col2.metric("Lotes Activos", len(prod_batches))
col3.metric("Precio de Venta", f"${df_products[df_products['id']==prod_id]['selling_price'].values[0]:,.2f}")

st.markdown("---")

# --- FILA 2: GRÁFICOS ANALÍTICOS ---
row2_col1, row2_col2 = st.columns([1, 1])

with row2_col1:
    st.subheader("Distribución de Cantidades por Lote")
    if not prod_batches.empty:
        fig_bar = px.bar(prod_batches, x='code', y='current_quantity', color='code',
                         text='current_quantity', template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No hay lotes disponibles para este producto.")

with row2_col2:
    st.subheader("Estado de Vencimiento")
    if not prod_batches.empty:
        prod_batches['expiration_date'] = pd.to_datetime(prod_batches['expiration_date'])
        fig_line = px.scatter(prod_batches, x='expiration_date', y='current_quantity', 
                              size='current_quantity', color='code', template="plotly_dark")
        st.plotly_chart(fig_line, use_container_width=True)

# --- FILA 3: TABLA DE DETALLE ---
st.subheader("Detalle de Lotes")
st.dataframe(prod_batches.rename(columns={
    'code': 'Código Lote', 
    'current_quantity': 'Cantidad Disponible', 
    'expiration_date': 'Fecha Vencimiento'
}), use_container_width=True)