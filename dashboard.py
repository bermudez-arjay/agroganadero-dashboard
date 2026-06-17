import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURACIÓN & ESTILOS PREMIUM
# ==============================================================================
st.set_page_config(page_title="Dashboard Gerencial", page_icon="📊", layout="wide")

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
# 2. CAPA DE CONEXIÓN
# ==============================================================================
@st.cache_data(ttl=60)
def fetch_api_data():
    try:
        response = requests.get("http://52.162.39.199:8080/api/Dashboard/strategic", timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Error: {e}")
        return None

data = fetch_api_data()
if not data: st.stop()

# Procesamiento
sales_trend = pd.DataFrame(data['salesTrend'])
sales_trend['date'] = pd.to_datetime(sales_trend['date'])
df_alerts = pd.DataFrame(data['expirationAlerts'])
df_stock = pd.DataFrame(data['productStockLevels'])
df_risk = pd.DataFrame(data['creditRisk'])

# ==============================================================================
# 3. CONSTRUCCIÓN DEL DASHBOARD GERENCIAL
# ==============================================================================
st.markdown("## Dashboard Gerencial")

# --- FILA 1: KPIs ---
kpi_cols = st.columns(4)

with kpi_cols[0]:
    st.markdown(f"""<div class="executive-container"><div class="section-title">Ingresos Totales</div>
    <div class="main-metric">C${data['totalRevenue']:,.2f}</div></div>""", unsafe_allow_html=True)
    # Sparkline del primer KPI
    fig_s = go.Figure(go.Scatter(y=sales_trend['amount'], mode='lines', line=dict(color='#00e676', width=2)))
    fig_s.update_layout(height=40, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis=dict(visible=False), yaxis=dict(visible=False))
    st.plotly_chart(fig_s, use_container_width=True, config={'displayModeBar': False})

with kpi_cols[1]:
    st.markdown(f"""<div class="executive-container" style="height:127px;"><div class="section-title">Cartera Concedida</div>
    <div class="main-metric">C${data['totalCreditGranted']:,.2f}</div></div>""", unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""<div class="executive-container" style="height:127px; border-left: 4px solid #ff5252;"><div class="section-title">Riesgo en Calle</div>
    <div class="main-metric" style="color: #ff5252;">C${data['totalPendingRisk']:,.2f}</div></div>""", unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""<div class="executive-container" style="height:127px;"><div class="section-title">Clientes Activos</div>
    <div class="main-metric">{data['activeCustomersCount']}</div></div>""", unsafe_allow_html=True)

# --- FILA 2: GRÁFICOS ---
r2_c1, r2_c2, r2_c3 = st.columns([1, 1.5, 1])

with r2_c1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Distribución de Riesgo</div>", unsafe_allow_html=True)
    fig_pie = px.pie(df_risk, values='amount', names='status', hole=0.7, color_discrete_map={'PENDING': '#ffb300'})
    fig_pie.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_pie, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2_c2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Tendencia Cierre de Ventas</div>", unsafe_allow_html=True)
    fig_bar = px.bar(sales_trend, x='date', y='amount', color_discrete_sequence=['#00b0ff'])
    fig_bar.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2_c3:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Índice de Salud Financiera</div>", unsafe_allow_html=True)
    fig_g = go.Figure(go.Indicator(mode="gauge+number", value=data['recoveryRate'], gauge={'bar': {'color': "#00e676"}, 'axis': {'range': [0, 100]}}))
    fig_g.update_layout(height=230, margin=dict(l=20, r=20, t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- FILA 3: TABLAS Y STOCK ---
r3_c1, r3_c2 = st.columns([1, 2])
with r3_c1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Alertas Críticas</div>", unsafe_allow_html=True)
    st.dataframe(df_alerts.rename(columns={'productName': 'Producto', 'expirationDate': 'Vence'}), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r3_c2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Stock por Lote</div>", unsafe_allow_html=True)
    fig_st = px.bar(df_stock, x='productName', y='currentQuantity', color='batchCode')
    fig_st.update_layout(height=250, margin=dict(l=10, r=10, t=10, b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_st, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
