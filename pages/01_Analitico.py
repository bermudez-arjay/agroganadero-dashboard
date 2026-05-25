import streamlit as st
import plotly.express as px
from utils import fetch_production_data

st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

st.title("📈 Dashboard Táctico de Ventas")

# --- 1. JERARQUÍA VISUAL (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"C${df_sales['total_amount'].sum():,.2f}")
col2.metric("Stock Global", f"{df_batches['current_quantity'].sum():,.0f}")
col3.metric("Cartera Pendiente", f"C${df_credits['pending_balance'].sum():,.2f}")
col4.metric("Clientes Activos", len(df_customers))

st.markdown("---")

# --- 2. ANÁLISIS PRINCIPAL ---
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Ventas por Vendedor")
    sales_by_vendor = df_sales.groupby('vendor_name')['total_amount'].sum().reset_index()
    fig_bar = px.bar(sales_by_vendor, x='vendor_name', y='total_amount', template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

with row1_c2:
    st.subheader("Distribución de Estados de Lote")
    fig_pie = px.pie(df_batches, names='state', hole=0.5, template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. NUEVA VISUALIZACIÓN TÁCTICA (Reemplazo de la tabla) ---
st.subheader("Composición de Productos por Valor de Venta")
# Usamos un Treemap para mostrar jerarquía y volumen sin saturar
fig_tree = px.treemap(df_products, 
                      path=['name'], 
                      values='selling_price',
                      template="plotly_dark")
st.plotly_chart(fig_tree, use_container_width=True)

# --- 4. STORYTELLING: ESTRUCTURA DE DECISIÓN ---
with st.expander("💡 Análisis Táctico"):
    st.write("**Contexto:** Evaluación de la cartera de productos y desempeño comercial.")
    st.write("**Evidencia:** El Treemap visualiza qué productos dominan el valor de venta.")
    st.write("**Insight:** Existe una brecha entre los productos de mayor valor y su rotación real.")
    st.write("**Decisión:** Reenfocar la estrategia de ventas hacia los productos de alta rotación identificados en los lotes.")