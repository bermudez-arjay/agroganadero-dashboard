import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURACIÓN & ESTILOS PROFESIONALES
# ==============================================================================
st.set_page_config(page_title="Dashboard Gerencial", page_icon="", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #0b0f19; }
        .executive-container { 
            background: linear-gradient(145deg, #161c2e, #111625);
            padding: 20px; border-radius: 12px; border: 1px solid #2a3558;
            margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
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
    try:
        response = requests.get("http://52.162.39.199:8080/api/Dashboard/strategic", timeout=10)
        return response.json()
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

data = fetch_api_data()
if not data: st.stop()

# ==============================================================================
# 3. CONSTRUCCIÓN DEL DASHBOARD
# ==============================================================================
st.markdown("## 📊 Dashboard Gerencial")

# --- FILA 1: KPIs ---
kpi_cols = st.columns(4)
kpis = [
    ("Ingresos Totales", f"C${data.get('totalRevenue', 0):,.2f}", "#3498db"),
    ("Cartera Concedida", f"C${data.get('totalCreditGranted', 0):,.2f}", "#3498db"),
    ("Riesgo en Calle", f"C${data.get('totalPendingRisk', 0):,.2f}", "#ff5252"),
    ("Clientes Activos", f"{data.get('activeCustomersCount', 0)}", "#e040fb")
]

for i, col in enumerate(kpi_cols):
    with col:
        st.markdown(f"""
            <div class="executive-container">
                <div class="section-title">{kpis[i][0]}</div>
                <div class="main-metric" style="color: {kpis[i][2] if i >= 2 else '#ffffff'}">{kpis[i][1]}</div>
            </div>
        """, unsafe_allow_html=True)

# --- FILA 2: GRÁFICOS ---
r2_c1, r2_c2, r2_c3 = st.columns([1, 1.5, 1])

with r2_c1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("### Distribución de Riesgo")
    df_risk = pd.DataFrame(data.get('creditRisk', []))
    if not df_risk.empty and 'amount' in df_risk.columns:
        fig_pie = px.pie(df_risk, values='amount', names='status', hole=0.7, 
                         color_discrete_sequence=['#ffb300'])
        fig_pie.update_layout(height=250, margin=dict(t=0, b=0, l=0, r=0), 
                              paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_pie, use_container_width=True)
    else: st.info("Sin datos de riesgo")
    st.markdown("</div>", unsafe_allow_html=True)

with r2_c2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("### Tendencia Cierre de Ventas")
    df_trend = pd.DataFrame(data.get('salesTrend', []))
    if not df_trend.empty:
        fig_bar = px.bar(df_trend, x='date', y='amount', color_discrete_sequence=['#00b0ff'])
        fig_bar.update_layout(height=250, margin=dict(t=10, b=0), 
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2_c3:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("### Índice de Salud Financiera")
    fig_g = go.Figure(go.Indicator(mode="gauge+number", value=data.get('recoveryRate', 0), 
                      gauge={'bar': {'color': "#00e676"}, 'axis': {'range': [0, 100]}}))
    fig_g.update_layout(height=230, margin=dict(t=20, b=20), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_g, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- FILA 3: ALERTAS Y STOCK ---
r3_c1, r3_c2 = st.columns([1, 2])
with r3_c1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("### 🚨 Alertas de Vencimiento")
    st.dataframe(pd.DataFrame(data.get('expirationAlerts', [])), use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r3_c2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("### 📦 Stock por Lote")
    df_stock = pd.DataFrame(data.get('productStockLevels', []))
    if not df_stock.empty:
        fig_st = px.bar(df_stock, x='productName', y='currentQuantity', color='batchCode', barmode='stack')
        fig_st.update_layout(height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_st, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
