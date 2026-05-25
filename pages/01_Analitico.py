import streamlit as st
import plotly.express as px
import pandas as pd
from utils import fetch_production_data

st.set_page_config(page_title="Dashboard Táctico", layout="wide")

df_sales, df_purchases, df_credits, df_batches, df_products = fetch_production_data()

st.title("📊 Dashboard Táctico")

# --- 1. KPI PRINCIPALES ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Ventas Totales", f"C${df_sales['total_amount'].sum():,.2f}")
c2.metric("Inversión Compras", f"C${df_purchases['total_amount'].sum():,.2f}")
c3.metric("Stock en Lotes", f"{df_batches['current_quantity'].sum():,.0f}")
c4.metric("Cartera Pendiente", f"C${df_credits['pending_balance'].sum():,.2f}")

st.markdown("---")

# --- 2. VISTA DE FLUJO (Ventas vs Compras) ---
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Tendencia: Ventas vs Compras")
    df_sales['date'] = pd.to_datetime(df_sales['created_at']).dt.date
    df_purchases['date'] = pd.to_datetime(df_purchases['purchase_date']).dt.date
    
    daily_s = df_sales.groupby('date')['total_amount'].sum().reset_index().rename(columns={'total_amount': 'Ventas'})
    daily_p = df_purchases.groupby('date')['total_amount'].sum().reset_index().rename(columns={'total_amount': 'Compras'})
    
    fig_line = px.line(pd.merge(daily_s, daily_p, on='date', how='outer').fillna(0), 
                       x='date', y=['Ventas', 'Compras'], template="plotly_dark")
    st.plotly_chart(fig_line, use_container_width=True)

with row1_c2:
    st.subheader("Distribución de Lote por Estados")
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

# --- 4. NUEVO: TREEMAP DE PRODUCTOS ---
st.subheader("Jerarquía de Productos por Valor de Venta")
fig_tree = px.treemap(
    df_products, 
    path=['name'], 
    values='selling_price',
    color='selling_price',
    color_continuous_scale='RdBu',
    template="plotly_dark"
)
st.plotly_chart(fig_tree, use_container_width=True)
