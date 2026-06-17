import streamlit as st
import plotly.express as px
import pandas as pd
import requests

st.set_page_config(page_title="Dashboard Táctico", layout="wide")

# --- Función de Fetching desde API ---
@st.cache_data(ttl=60)
def fetch_tactical_data():
    try:
        response = requests.get("http://52.162.39.199:8080/api/Dashboard/tactical", timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Error conectando a la API: {e}")
        return None

data = fetch_tactical_data()

if not data:
    st.stop()

# --- Transformación a DataFrames ---
df_sales_trend = pd.DataFrame(data['salesTrend'])
df_purchases_trend = pd.DataFrame(data['purchasesTrend'])
df_batches = pd.DataFrame(data['batchStates'])
df_vendor = pd.DataFrame(data['salesByVendor'])
df_supplier = pd.DataFrame(data['purchasesBySupplier'])
df_products = pd.DataFrame(data['productHierarchy'])

# Función de Tarjetas KPI
def kpi_card(title, value, description, color):
    st.markdown(f"""
    <div style="background-color: #1e2536; padding: 20px; border-radius: 10px; border-left: 5px solid {color};">
        <p style="color: #8899a6; margin: 0; font-size: 14px;">{title}</p>
        <h2 style="color: white; margin: 5px 0;">{value}</h2>
        <p style="color: {color}; margin: 0; font-size: 14px;">▲ {description}</p>
    </div>
    """, unsafe_allow_html=True)

st.title("📊 Dashboard Táctico")

# --- 1. KPI PRINCIPALES ---
k1, k2, k3, k4 = st.columns(4)
with k1: kpi_card("INGRESOS (VENTAS)", f"C${data['totalSales']:,.2f}", "Crecimiento Operativo", "#3498db")
with k2: kpi_card("INVERSIÓN (COMPRAS)", f"C${data['totalPurchases']:,.2f}", "Flujo de Abastecimiento", "#e74c3c")
with k3: kpi_card("STOCK GLOBAL", f"{data['globalStock']:,} Unid.", "Disponibilidad Total", "#2ecc71")
with k4: kpi_card("CARTERA PENDIENTE", f"C${data['pendingCredits']:,.2f}", "Saldo por Cobrar", "#3498db")

st.markdown("---")

# --- 2. VISTA DE FLUJO ---
row1_c1, row1_c2 = st.columns([2, 1])

with row1_c1:
    st.subheader("Tendencia: Ventas vs Compras")
    # Merge de tendencias
    df_sales_trend['date'] = pd.to_datetime(df_sales_trend['date'])
    df_purchases_trend['date'] = pd.to_datetime(df_purchases_trend['date'])
    
    # Combinar para gráfico
    merged = pd.merge(df_sales_trend.rename(columns={'amount': 'Ventas'}), 
                      df_purchases_trend.rename(columns={'amount': 'Compras'}), 
                      on='date', how='outer').fillna(0)
    
    fig_line = px.line(merged, x='date', y=['Ventas', 'Compras'], template="plotly_dark",
                       color_discrete_map={"Ventas": "#3498db", "Compras": "#e74c3c"})
    st.plotly_chart(fig_line, use_container_width=True)

with row1_c2:
    st.subheader("Estados de Lote")
    fig_pie = px.pie(df_batches, values='count', names='state', hole=0.5, template="plotly_dark",
                     color_discrete_sequence=["#2ecc71", "#e74c3c", "#3498db"])
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 3. RENDIMIENTO ---
row2_c1, row2_c2 = st.columns(2)
with row2_c1:
    st.subheader("Ventas por Vendedor")
    fig_bar = px.bar(df_vendor, x='vendor', y='amount', template="plotly_dark", color_discrete_sequence=["#3498db"])
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_c2:
    st.subheader("Compras por Proveedor")
    fig_bar_p = px.bar(df_supplier, x='supplier', y='amount', template="plotly_dark", color_discrete_sequence=["#e74c3c"])
    st.plotly_chart(fig_bar_p, use_container_width=True)

# --- 4. TREEMAP ---
st.subheader("Jerarquía de Productos (Valor de Venta)")
fig_tree = px.treemap(
    df_products, 
    path=['name'], 
    values='price',
    color='price',
    color_continuous_scale=["#e74c3c", "#3498db", "#2ecc71"],
    template="plotly_dark"
)
st.plotly_chart(fig_tree, use_container_width=True)
