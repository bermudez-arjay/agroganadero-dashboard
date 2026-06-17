import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURACIÓN (MANTENIDA)
# ==============================================================================
st.set_page_config(page_title="Executive Performance Dashboard", page_icon="📊", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #111625; color: #ffffff; }
        .executive-container { background-color: #1e2640; border-radius: 8px; padding: 1.25rem; border: 1px solid #2a3558; margin-bottom: 1rem; }
        .section-title { font-size: 0.85rem; color: #8fa0dd; text-transform: uppercase; margin-bottom: 0.5rem; }
        .main-metric { font-size: 2rem; font-weight: 700; color: #ffffff; }
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CAPA DE CONEXIÓN A API
# ==============================================================================
@st.cache_data(ttl=60)
def fetch_api_data():
    url = "http://52.162.39.199:8080/api/Dashboard/strategic"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error conectando a la API: {e}")
        return None

data = fetch_api_data()

if not data:
    st.stop()

# --- Transformación a DataFrames para compatibilidad con tu lógica ---
sales_trend = pd.DataFrame(data['salesTrend'])
sales_trend['date'] = pd.to_datetime(sales_trend['date'])

df_alerts = pd.DataFrame(data['expirationAlerts'])
df_stock = pd.DataFrame(data['productStockLevels'])
df_credit_risk = pd.DataFrame(data['creditRisk'])

# ==============================================================================
# 3. CONSTRUCCIÓN DE LA INTERFAZ (ADAPTADA)
# ==============================================================================

# --- FILA 1: KPIs FINANCIEROS ---
kpi_cols = st.columns(4)

with kpi_cols[0]:
    st.markdown(f"""
        <div class="executive-container"><div class="section-title">Ingresos Totales</div>
        <div class="main-metric">C${data['totalRevenue']:,.2f}</div></div>
    """, unsafe_allow_html=True)

with kpi_cols[1]:
    st.markdown(f"""
        <div class="executive-container"><div class="section-title">Cartera Concedida</div>
        <div class="main-metric">C${data['totalCreditGranted']:,.2f}</div></div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""
        <div class="executive-container" style="border-left: 4px solid #ff5252;">
        <div class="section-title">Riesgo en Calle</div>
        <div class="main-metric" style="color: #ff5252;">C${data['totalPendingRisk']:,.2f}</div></div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""
        <div class="executive-container"><div class="section-title">Clientes Activos</div>
        <div class="main-metric">{data['activeCustomersCount']}</div></div>
    """, unsafe_allow_html=True)

# --- FILA 2 ---
row2_col1, row2_col2, row2_col3 = st.columns([1, 1.5, 1])

with row2_col1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Distribución de Riesgo</div>", unsafe_allow_html=True)
    fig_pie = px.pie(df_credit_risk, values='amount', names='status', hole=0.6)
    fig_pie.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)', showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Tendencia de Ventas</div>", unsafe_allow_html=True)
    fig_trend = px.bar(sales_trend, x='date', y='amount')
    fig_trend.update_layout(height=280, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col3:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Índice de Salud Financiera</div>", unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=data['recoveryRate']))
    fig_gauge.update_layout(height=260, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- FILA 3 ---
row3_col1, row3_col2 = st.columns([1.2, 1.8])

with row3_col1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🚨 Alertas de Vencimiento</div>", unsafe_allow_html=True)
    st.dataframe(df_alerts, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with row3_col2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📦 Stock por Lote</div>", unsafe_allow_html=True)
    fig_stock = px.bar(df_stock, x='productName', y='currentQuantity', color='batchCode')
    fig_stock.update_layout(height=215, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_stock, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
