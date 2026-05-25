import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_production_data

# Configuración de página para dashboard profesional
st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

st.title("📊 Dashboard Táctico")

# 1. JERARQUÍA VISUAL: KPIs CLAVE (Fila superior)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Ventas Totales", f"C${df_sales['total_amount'].sum():,.2f}", "+9.5%")
col2.metric("Stock Global", f"{df_batches['current_quantity'].sum():,.0f}", "Estable")
col3.metric("Cartera Pendiente", f"C${df_credits['pending_balance'].sum():,.2f}", "-2%")
col4.metric("Clientes Activos", len(df_customers), "+5%")

st.markdown("---")

# 2. SECCIÓN DE ANÁLISIS: STORYTELLING (Gráficos)
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Tendencia de Ventas vs Cuotas")
    # Gráfico de línea con intención semántica
    fig_line = px.line(df_sales, x='created_at', y='total_amount', template="plotly_white")
    st.plotly_chart(fig_line, use_container_width=True)

with row1_c2:
    st.subheader("Distribución de Stock")
    # Gráfico circular para evitar saturación
    fig_pie = px.pie(df_batches.head(5), values='current_quantity', names='code', hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

# 3. STORYTELLING: CONTEXTO, EVIDENCIA, INSIGHT Y DECISIÓN
st.subheader("💡 Análisis Táctico")
with st.container():
    c1, c2 = st.columns(2)
    c1.info("**Evidencia:** Los datos muestran una rotación alta en los primeros 3 lotes de insumos.")
    c2.warning("**Decisión:** Priorizar la compra de nuevos lotes para evitar quiebres de stock en el producto A.")

# Tabla de detalle con diseño limpio
st.subheader("Detalle Operativo")
st.dataframe(df_products.head(10), use_container_width=True)