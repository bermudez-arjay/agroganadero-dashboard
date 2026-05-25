import streamlit as st
import plotly.express as px
from utils import fetch_production_data

st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

st.title("📈 Dashboard Táctico de Ventas")

# --- JERARQUÍA VISUAL (KPIs) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"C${df_sales['total_amount'].sum():,.2f}", "+9.5%")
col2.metric("Stock Global", f"{df_batches['current_quantity'].sum():,.0f}")
col3.metric("Cartera Pendiente", f"C${df_credits['pending_balance'].sum():,.2f}")
col4.metric("Clientes Activos", len(df_customers))

st.markdown("---")

# --- ANÁLISIS Y STORYTELLING ---
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Ventas por Vendedor")
    sales_by_vendor = df_sales.groupby('vendor_name')['total_amount'].sum().reset_index()
    fig = px.bar(sales_by_vendor, x='vendor_name', y='total_amount', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

with row1_c2:
    st.subheader("Estado de Lotes")
    fig_pie = px.pie(df_batches, names='state', hole=0.5, template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

# --- STORYTELLING: CONTEXTO, EVIDENCIA, INSIGHT, DECISIÓN ---
with st.expander("💡 Análisis Táctico"):
    st.write("**Contexto:** Revisión de desempeño comercial y operativo (Nov 2024).")
    st.write("**Evidencia:** El volumen de ventas está concentrado en pocos vendedores.")
    st.write("**Insight:** Se observa una tasa de cumplimiento de cuota variable por vendedor.")
    st.write("**Decisión:** Implementar sesiones de capacitación enfocadas en el vendedor con menor rendimiento.")

# --- DETALLE OPERATIVO ---
st.subheader("Detalle de Productos")
st.dataframe(df_products, use_container_width=True)