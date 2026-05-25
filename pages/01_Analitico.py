import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_production_data

st.set_page_config(page_title="Análisis de Operaciones", layout="wide")

# Estilos ejecutivos oscuros
st.markdown("""
    <style>
        .stApp { background-color: #111625; }
        h1, h2, h3 { color: #ffffff !important; }
        .metric-card { background-color: #1e2640; padding: 20px; border-radius: 10px; border: 1px solid #2a3558; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Análisis Profundo de Operaciones")

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

# --- FILTROS SUPERIORES ---
col_f1, col_f2 = st.columns([1, 3])
with col_f1:
    selected_product = st.selectbox("Seleccionar Insumo:", df_products['name'].unique())

# Filtrar datos del producto seleccionado
prod_id = df_products[df_products['name'] == selected_product]['id'].iloc[0]
prod_batches = df_batches[df_batches['product_id'] == prod_id]

# --- FILA 1: KPIs RESUMEN ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
total_stock = prod_batches['current_quantity'].sum()
kpi1.metric("Stock Total", f"{total_stock} Unidades")
kpi2.metric("Lotes Activos", len(prod_batches))
kpi3.metric("Precio Venta", f"C${df_products[df_products['id']==prod_id]['selling_price'].values[0]:,.2f}")
kpi4.metric("Valor Inventario", f"C${(total_stock * df_products[df_products['id']==prod_id]['purchase_price'].values[0]):,.2f}")

st.markdown("---")

# --- FILA 2: GRÁFICOS ANALÍTICOS ---
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Distribución de Stock por Lote")
    fig_bar = px.bar(prod_batches, x='code', y='current_quantity', color='code', 
                     template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_bar.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("Cronograma de Vencimiento")
    fig_line = px.scatter(prod_batches, x='expiration_date', y='current_quantity', 
                          size='current_quantity', color='state', 
                          template="plotly_dark", color_discrete_sequence=['#00e676'])
    fig_line.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

# --- TABLA DETALLADA ---
st.subheader("Detalle de Inventario")
st.dataframe(
    prod_batches[['code', 'current_quantity', 'expiration_date', 'state']]
    .rename(columns={'code': 'Lote', 'current_quantity': 'Stock', 'expiration_date': 'Vencimiento', 'state': 'Estado'}),
    use_container_width=True
)