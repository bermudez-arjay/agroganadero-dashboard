import streamlit as st
import plotly.express as px
import pandas as pd
from utils import fetch_production_data

st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# Función de Tarjetas KPI con colores personalizados
def kpi_card(title, value, description, color):
    st.markdown(f"""
    <div style="background-color: #1e2536; padding: 20px; border-radius: 10px; border-left: 5px solid {color};">
        <p style="color: #8899a6; margin: 0; font-size: 14px;">{title}</p>
        <h2 style="color: white; margin: 5px 0;">{value}</h2>
        <p style="color: {color}; margin: 0; font-size: 14px;">▲ {description}</p>
    </div>
    """, unsafe_allow_html=True)

df_sales, df_purchases, df_credits, df_batches, df_products = fetch_production_data()

st.title("📊 Dashboard Táctico")

# --- 1. KPI PRINCIPALES (Paleta: Azul, Rojo, Verde) ---
k1, k2, k3, k4 = st.columns(4)
with k1: kpi_card("INGRESOS (VENTAS)", f"C${df_sales['total_amount'].sum():,.2f}", "Crecimiento Operativo", "#3498db") # Azul
with k2: kpi_card("INVERSIÓN (COMPRAS)", f"C${df_purchases['total_amount'].sum():,.2f}", "Flujo de Abastecimiento", "#e74c3c") # Rojo
with k3: kpi_card("STOCK GLOBAL", f"{df_batches['current_quantity'].sum():,.0f} Unid.", "Disponibilidad Total", "#2ecc71") # Verde
with k4: kpi_card("CARTERA PENDIENTE", f"C${df_credits['pending_balance'].sum():,.2f}", "Saldo por Cobrar", "#3498db") # Azul

st.markdown("---")

# --- 2. VISTA DE FLUJO (Ventas vs Compras) ---
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Tendencia: Ventas (Azul) vs Compras (Rojo)")
    df_sales['date'] = pd.to_datetime(df_sales['created_at']).dt.date
    df_purchases['date'] = pd.to_datetime(df_purchases['purchase_date']).dt.date
    
    daily_s = df_sales.groupby('date')['total_amount'].sum().reset_index().rename(columns={'total_amount': 'Ventas'})
    daily_p = df_purchases.groupby('date')['total_amount'].sum().reset_index().rename(columns={'total_amount': 'Compras'})
    
    fig_line = px.line(pd.merge(daily_s, daily_p, on='date', how='outer').fillna(0), 
                       x='date', y=['Ventas', 'Compras'], template="plotly_dark",
                       color_discrete_map={"Ventas": "#3498db", "Compras": "#e74c3c"})
    st.plotly_chart(fig_line, use_container_width=True)

with row1_c2:
    st.subheader("Estados de Lote")
    fig_pie = px.pie(df_batches, names='state', hole=0.5, template="plotly_dark",
                     color_discrete_sequence=["#2ecc71", "#e74c3c", "#3498db"])
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. RENDIMIENTO ---
row2_c1, row2_c2 = st.columns(2)
with row2_c1:
    st.subheader("Ventas por Vendedor")
    fig_bar = px.bar(df_sales.groupby('vendor_name')['total_amount'].sum().reset_index(), 
                     x='vendor_name', y='total_amount', template="plotly_dark", color_discrete_sequence=["#3498db"])
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_c2:
    st.subheader("Compras por Proveedor")
    fig_bar_p = px.bar(df_purchases.groupby('supplier_name')['total_amount'].sum().reset_index(), 
                       x='supplier_name', y='total_amount', template="plotly_dark", color_discrete_sequence=["#e74c3c"])
    st.plotly_chart(fig_bar_p, use_container_width=True)

# --- 4. TREEMAP (Jerarquía de Productos) ---
st.subheader("Jerarquía de Productos (Valor de Venta)")
fig_tree = px.treemap(
    df_products, 
    path=['name'], 
    values='selling_price',
    color='selling_price',
    color_continuous_scale=["#e74c3c", "#3498db", "#2ecc71"], # Rojo a Azul a Verde
    template="plotly_dark"
)
st.plotly_chart(fig_tree, use_container_width=True)
