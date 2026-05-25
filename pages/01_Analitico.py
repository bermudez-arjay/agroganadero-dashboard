import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_production_data

# Configuración de página
st.set_page_config(page_title="Dashboard Analítico", layout="wide")

# Estilos ejecutivos oscuros
st.markdown("""
    <style>
        .stApp { background-color: #0e1117; }
        .metric-card { 
            background-color: #1e2640; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #2a3558; 
            text-align: center;
        }
        h1, h2, h3 { color: #ffffff !important; }
    </style>
""", unsafe_allow_html=True)

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

st.title("📊 Análisis Profundo de Operaciones")

# --- FILA 1: KPIs RESUMEN EJECUTIVO ---
st.subheader("Resumen de Rendimiento Global")
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f'<div class="metric-card"><h3>Ventas</h3><h1>C${df_sales["total_amount"].sum():,.0f}</h1></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="metric-card"><h3>Stock Total</h3><h1>{df_batches["current_quantity"].sum():,.0f}</h1></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="metric-card"><h3>Cartera Activa</h3><h1>C${df_credits["pending_balance"].sum():,.0f}</h1></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="metric-card"><h3>Clientes</h3><h1>{len(df_customers)}</h1></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- FILTRO Y ANÁLISIS POR PRODUCTO ---
st.sidebar.header("Análisis por Insumo")
selected_product = st.sidebar.selectbox("Seleccionar Insumo:", df_products['name'].unique())

# Obtener datos del producto seleccionado
prod_row = df_products[df_products['name'] == selected_product].iloc[0]
prod_batches = df_batches[df_batches['product_id'] == prod_row['id']]

st.subheader(f"Detalle Operativo: {selected_product}")

# Fila de visualización táctica
row2_c1, row2_c2 = st.columns([1, 2])

with row2_c1:
    st.metric("Precio de Venta", f"C${prod_row['selling_price']:,.2f}")
    st.metric("Lotes en Inventario", len(prod_batches))
    st.write("Estado de Lotes:")
    fig_pie = px.pie(prod_batches, names='state', hole=0.5, template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

with row2_c2:
    st.subheader("Distribución de Cantidades por Lote")
    fig_bar = px.bar(prod_batches, x='code', y='current_quantity', 
                     text='current_quantity', template="plotly_dark")
    fig_bar.update_traces(marker_color='#00e676')
    st.plotly_chart(fig_bar, use_container_width=True)

# Tabla final de detalle
st.subheader("Registros de Lote")
st.dataframe(prod_batches[['code', 'current_quantity', 'expiration_date', 'state']], 
             use_container_width=True, hide_index=True)