import streamlit as st
import plotly.express as px
import pandas as pd
from utils import fetch_production_data

# Configuración de página
st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# Estilos CSS para los KPIs (basados en tu referencia visual)
def kpi_card(title, value, description):
    st.markdown(f"""
    <div style="background-color: #1e2536; padding: 20px; border-radius: 10px; border-left: 5px solid #2ecc71;">
        <p style="color: #8899a6; margin: 0; font-size: 14px;">{title}</p>
        <h2 style="color: white; margin: 5px 0;">{value}</h2>
        <p style="color: #2ecc71; margin: 0; font-size: 14px;">▲ {description}</p>
    </div>
    """, unsafe_allow_html=True)

# Carga de datos
df_sales, df_purchases, df_credits, df_batches, df_products = fetch_production_data()

st.title("📊 Dashboard Táctico")

# --- 1. KPI PRINCIPALES (Estilizados) ---
k1, k2, k3, k4 = st.columns(4)

with k1:
    kpi_card("INGRESOS TOTALES", f"C${df_sales['total_amount'].sum():,.2f}", "En Crecimiento Operativo")
with k2:
    kpi_card("INVERSIÓN COMPRAS", f"C${df_purchases['total_amount'].sum():,.2f}", "Flujo de Abastecimiento")
with k3:
    kpi_card("STOCK GLOBAL", f"{df_batches['current_quantity'].sum():,.0f} Unid.", "Disponibilidad Actual")
with k4:
    kpi_card("CARTERA PENDIENTE", f"C${df_credits['pending_balance'].sum():,.2f}", "Saldo por Cobrar")

st.markdown("---")

# --- 2. VISTA DE FLUJO (Ventas vs Compras) ---
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Tendencia: Ventas vs. Compras")
    df_sales['date'] = pd.to_datetime(df_sales['created_at']).dt.date
    df_purchases['date'] = pd.to_datetime(df_purchases['purchase_date']).dt.date
    
    daily_s = df_sales.groupby('date')['total_amount'].sum().reset_index().rename(columns={'total_amount': 'Ventas'})
    daily_p = df_purchases.groupby('date')['total_amount'].sum().reset_index().rename(columns={'total_amount': 'Compras'})
    
    fig_line = px.line(pd.merge(daily_s, daily_p, on='date', how='outer').fillna(0), 
                       x='date', y=['Ventas', 'Compras'], template="plotly_dark")
    st.plotly_chart(fig_line, use_container_width=True)

with row1_c2:
    st.subheader("Distribución de Lotes")
    fig_pie = px.pie(df_batches, names='state', hole=0.5, template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. RENDIMIENTO (Vendedores y Proveedores) ---
row2_c1, row2_c2 = st.columns(2)
with row2_c1:
    st.subheader("Ventas por Vendedor")
    fig_bar = px.bar(df_sales.groupby('vendor_name')['total_amount'].sum().reset_index(), 
                     x='vendor_name', y='total_amount', template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_c2:
    st.subheader("Compras por Proveedor")
    fig_bar_p = px.bar(df_purchases.groupby('supplier_name')['total_amount'].sum().reset_index(), 
                       x='supplier_name', y='total_amount', color_discrete_sequence=['indianred'], template="plotly_dark")
    st.plotly_chart(fig_bar_p, use_container_width=True)

# --- 4. TREEMAP DE PRODUCTOS (Detalle jerárquico) ---
st.subheader("Jerarquía de Productos por Valor")
fig_tree = px.treemap(
    df_products, 
    path=['name'], 
    values='selling_price',
    color='selling_price',
    color_continuous_scale='RdBu',
    template="plotly_dark"
)
st.plotly_chart(fig_tree, use_container_width=True)

