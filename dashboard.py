import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURACIÓN DE PANTALLA & CONTROL DE TEMA OSCURO PREMIUM
# ==============================================================================
st.set_page_config(
    page_title="Executive Performance Dashboard | AgroGanadero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS mantenidos
st.markdown("""
    <style>
        .stApp { background-color: #111625; color: #ffffff; }
        .block-container { padding-top: 1rem; padding-bottom: 1rem; }
        .executive-container {
            background-color: #1e2640;
            border-radius: 8px;
            padding: 1.25rem;
            border: 1px solid #2a3558;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            margin-bottom: 1rem;
        }
        h1, h2, h3, h4, h5, h6 { color: #ffffff !important; font-family: 'Inter', sans-serif; font-weight: 600; }
        .section-title { font-size: 0.85rem; color: #8fa0dd; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; }
        .main-metric { font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0.2rem 0; }
        .metric-delta { font-size: 0.85rem; font-weight: 500; }
        .delta-positive { color: #00e676; }
        .delta-negative { color: #ff5252; }
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. CAPA DE CONEXIÓN A POSTGRESQL
# ==============================================================================
@st.cache_data(ttl=60)
def fetch_production_data():
    try:
        db_url = st.secrets["db_credentials"]["connection_string"]
        with psycopg2.connect(db_url) as conn:
            sales = pd.read_sql_query("SELECT total_amount, created_at FROM sales WHERE deleted_at IS NULL;", conn)
            credits = pd.read_sql_query("SELECT total_amount, pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
            batches = pd.read_sql_query("SELECT code, current_quantity, expiration_date, product_id FROM batches WHERE deleted_at IS NULL;", conn)
            customers = pd.read_sql_query("SELECT id FROM customers WHERE deleted_at IS NULL;", conn)
            products = pd.read_sql_query("SELECT id, name FROM products WHERE deleted_at IS NULL;", conn)
        return sales, credits, batches, customers, products
    except Exception as e:
        st.error(f"Error de Infraestructura: {e}")
        return [pd.DataFrame()] * 5

df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

if df_sales.empty or df_credits.empty:
    st.error("Almacén de datos vacío o inaccesible.")
    st.stop()

# Procesamiento
df_sales['fecha'] = pd.to_datetime(df_sales['created_at']).dt.date
sales_trend = df_sales.groupby('fecha')['total_amount'].sum().reset_index().sort_values('fecha')

# Mapeo de Estados para el gráfico
status_map = {'PAID': 'Pagado', 'ACTIVE': 'Activo', 'OVERDUE': 'Vencido'}
df_credits['status_label'] = df_credits['status'].map(status_map)

# ==============================================================================
# 3. CONSTRUCCIÓN DE LA INTERFAZ
# ==============================================================================

# Encabezado con nuevo título
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("<h2 style='margin:0;'>DASHBOARD GERENCIAL</h2>", unsafe_allow_html=True)
with header_col2:
    st.download_button("📥 EXPORTAR DATA AUDIT", data=df_sales.to_csv(index=False), file_name="Data_Audit.csv", use_container_width=True)

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# Fila 1: KPIs
kpi_cols = st.columns([1, 1, 1, 1])
with kpi_cols[0]:
    st.markdown(f'<div class="executive-container"><div class="section-title">Ingresos Totales</div><div class="main-metric">${df_sales["total_amount"].sum():,.2f}</div></div>', unsafe_allow_html=True)
with kpi_cols[1]:
    st.markdown(f'<div class="executive-container" style="height: 110px;"><div class="section-title">Cartera Concedida</div><div class="main-metric">${df_credits["total_amount"].sum():,.2f}</div></div>', unsafe_allow_html=True)
with kpi_cols[2]:
    st.markdown(f'<div class="executive-container" style="height: 110px; border-left: 4px solid #ff5252;"><div class="section-title">Riesgo en Calle</div><div class="main-metric" style="color: #ff5252;">${df_credits["pending_balance"].sum():,.2f}</div></div>', unsafe_allow_html=True)
with kpi_cols[3]:
    st.markdown(f'<div class="executive-container" style="height: 110px;"><div class="section-title">Clientes Activos</div><div class="main-metric">{df_customers["id"].nunique()}</div></div>', unsafe_allow_html=True)

# Fila 2: Gráficos con estados traducidos
row2_col1, row2_col2, row2_col3 = st.columns([1, 1.5, 1])

with row2_col1:
    st.markdown("<div class='executive-container'><div class='section-title'>Distribución de Riesgo de Crédito</div>", unsafe_allow_html=True)
    fig_pie = px.pie(
        df_credits.groupby('status_label')['total_amount'].sum().reset_index(), 
        values='total_amount', names='status_label', hole=0.6,
        color='status_label',
        color_discrete_map={'Pagado': '#00e676', 'Activo': '#ffb300', 'Vencido': '#ff5252'}
    )
    fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), margin=dict(l=10, r=10, t=10, b=10), height=250, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# ... (El resto de los gráficos mantienen tu lógica original)
with row2_col2:
    st.markdown("<div class='executive-container'><div class='section-title'>Tendencia Cierre de Ventas</div>", unsafe_allow_html=True)
    fig_trend = px.bar(sales_trend, x='fecha', y='total_amount')
    fig_trend.update_traces(marker_color='#00b0ff')
    fig_trend.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=250, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(showgrid=True, gridcolor='#2a3558'))
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col3:
    st.markdown("<div class='executive-container'><div class='section-title'>Índice de Salud Financiera</div>", unsafe_allow_html=True)
    fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=85, gauge={'bar': {'color': "#00e676"}, 'bgcolor': "#111625"}))
    fig_gauge.update_layout(margin=dict(l=20, r=20, t=30, b=10), height=230, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)