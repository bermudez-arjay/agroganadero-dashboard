import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_production_data

st.set_page_config(page_title="Dashboard Analítico", layout="wide")

# Inyectar estilos para mantener la coherencia visual con el principal
st.markdown("""
    <style>
        .stApp { background-color: #111625; }
        h1, h2, h3 { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 📊 Análisis Profundo de Operaciones")

# Carga de datos
_, _, df_batches, _, df_products = fetch_production_data()

# --- FILTROS ---
st.sidebar.header("Filtros de Análisis")
if not df_products.empty:
    selected_product = st.sidebar.selectbox("Seleccionar Insumo:", df_products['name'].unique())

    # --- FILA 1: KPIs DE PRODUCTO ---
    col1, col2, col3 = st.columns(3)

    prod_row = df_products[df_products['name'] == selected_product].iloc[0]
    prod_id = prod_row['id']
    prod_batches = df_batches[df_batches['product_id'] == prod_id]
    total_stock = prod_batches['current_quantity'].sum()

    col1.metric("Stock Actual", f"{total_stock} Unidades")
    col2.metric("Lotes Activos", len(prod_batches))
    col3.metric("Precio de Venta", f"C${prod_row['selling_price']:,.2f}")

    st.markdown("---")

    # --- FILA 2 ---
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.subheader("Distribución de Cantidades por Lote")
        fig_bar = px.bar(prod_batches, x='code', y='current_quantity', color='code', template="plotly_dark")
        st.plotly_chart(fig_bar, use_container_width=True)

    with row2_col2:
        st.subheader("Cronograma de Vencimiento")
        if 'expiration_date' in prod_batches.columns:
            prod_batches['expiration_date'] = pd.to_datetime(prod_batches['expiration_date'])
            fig_line = px.scatter(prod_batches, x='expiration_date', y='current_quantity', 
                                  size='current_quantity', color='code', template="plotly_dark")
            st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("Detalle de Lotes")
    st.dataframe(prod_batches.rename(columns={'code': 'Lote', 'current_quantity': 'Stock', 'expiration_date': 'Vencimiento'}), use_container_width=True)
else:
    st.warning("No hay productos cargados en la base de datos.")