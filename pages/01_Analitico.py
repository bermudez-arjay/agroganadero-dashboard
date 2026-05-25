import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# Carga
df_sales, df_credits, df_batches, df_products = fetch_production_data()

st.title("📊 Dashboard Táctico: Rendimiento Operativo")

# --- SECCIÓN 1: KPIs (Jerarquía Visual Clara) ---
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Ventas Totales", f"C${df_sales['total_amount'].sum():,.2f}")
kpi2.metric("Pendiente de Cobro", f"C${df_credits['pending_balance'].sum():,.2f}")
kpi3.metric("Stock Total", f"{df_batches['current_quantity'].sum():,.0f}")

st.markdown("---")

# --- SECCIÓN 2: VISUALIZACIONES (3 a 5 widgets) ---
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    st.subheader("Ventas por Vendedor")
    fig_bar = px.bar(df_sales.groupby('vendor_name')['total_amount'].sum().reset_index(), 
                     x='vendor_name', y='total_amount', color='total_amount', color_continuous_scale='teal')
    st.plotly_chart(fig_bar, use_container_width=True)

with row1_col2:
    st.subheader("Distribución de Estados")
    fig_pie = px.pie(df_batches, names='state', hole=0.6)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- SECCIÓN 3: STORYTELLING (Contexto a Decisión) ---
with st.container():
    st.subheader("💡 Análisis Táctico")
    col_st1, col_st2 = st.columns(2)
    col_st1.write("**Contexto & Evidencia:** El 70% de las ventas proviene de 3 vendedores clave, mientras que el stock muestra alta rotación.")
    col_st2.write("**Insight & Decisión:** Se recomienda incentivar al equipo de ventas restante y reabastecer el insumo más vendido (Beta 10).")

# --- SECCIÓN 4: DETALLE (Evitar saturación) ---
with st.expander("Ver detalle de productos"):
    st.dataframe(df_products, use_container_width=True)