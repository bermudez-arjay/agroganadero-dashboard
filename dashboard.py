import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ==============================================================================
# 1. CONFIGURACIÓN DE PANTALLA & CONTROL DE TEMA OSCURO PREMIUM
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Gerencial | AgroGanadero",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inyección de estilos CSS para mantener tu diseño ejecutivo
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
# 2. CAPA DE CONEXIÓN OPTIMIZADA A POSTGRESQL
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
        st.error(f"Error de Infraestructura en Render: {e}")
        return [pd.DataFrame()] * 5

df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

if df_sales.empty or df_credits.empty:
    st.error("Almacén de datos vacío o inaccesible.")
    st.stop()

# Procesamiento de datos y traducciones
df_sales['fecha'] = pd.to_datetime(df_sales['created_at']).dt.date
sales_trend = df_sales.groupby('fecha')['total_amount'].sum().reset_index().sort_values('fecha')

# Mapeo de estados a español
status_map = {'PAID': 'Pagado', 'ACTIVE': 'Activo', 'OVERDUE': 'Vencido'}
df_credits['status_es'] = df_credits['status'].map(status_map)

# ==============================================================================
# 3. CONSTRUCCIÓN DE LA INTERFAZ EJECUTIVA
# ==============================================================================

# --- ENCABEZADO ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("<h2 style='margin:0;'>DASHBOARD GERENCIAL</h2>", unsafe_allow_html=True)
with header_col2:
    st.download_button("📥 EXPORTAR DATA AUDIT", data=df_sales.to_csv(index=False), file_name="Data_Audit.csv", use_container_width=True)

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# --- FILA 1: KPIs ---
kpi_cols = st.columns([1, 1, 1, 1])

with kpi_cols[0]:
    st.markdown(f"""<div class="executive-container" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;"><div class="section-title">Ingresos Totales (Ventas)</div><div class="main-metric">${df_sales['total_amount'].sum():,.2f}</div><div class="metric-delta delta-positive">▲ En Crecimiento Operativo</div></div>""", unsafe_allow_html=True)
    fig_spark = go.Figure(go.Scatter(x=sales_trend['fecha'], y=sales_trend['total_amount'], mode='lines', fill='tozeroy', line=dict(color='#00e676', width=1.5), fillcolor='rgba(0, 230, 118, 0.08)'))
    fig_spark.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(l=10, r=10, t=0, b=5), height=35, paper_bgcolor='#1e2640', plot_bgcolor='#1e2640')
    st.plotly_chart(fig_spark, use_container_width=True, config={'displayModeBar': False})

with kpi_cols[1]:
    st.markdown(f"""<div class="executive-container" style="height: 182px;"><div class="section-title">Cartera Concedida</div><div class="main-metric">${df_credits['total_amount'].sum():,.2f}</div><div class="metric-delta" style="color: #00b0ff;">● Línea de Crédito Activa</div></div>""", unsafe_allow_html=True)

with kpi_cols[2]:
    st.markdown(f"""<div class="executive-container" style="height: 182px; border-left: 4px solid #ff5252;"><div class="section-title">Riesgo en Calle (Por Cobrar)</div><div class="main-metric" style="color: #ff5252;">${df_credits['pending_balance'].sum():,.2f}</div><div class="metric-delta delta-negative">⚠️ Gestión de Cobro Requerida</div></div>""", unsafe_allow_html=True)

with kpi_cols[3]:
    st.markdown(f"""<div class="executive-container" style="height: 182px;"><div class="section-title">Clientes Activos</div><div class="main-metric" style="color: #e040fb;">{df_customers['id'].nunique()}</div><div class="metric-delta">Total de clientes registrados</div></div>""", unsafe_allow_html=True)

# --- FILA 2: GRÁFICOS ---
row2_col1, row2_col2, row2_col3 = st.columns([1, 1.5, 1])

with row2_col1:
    st.markdown("<div class='executive-container'><div class='section-title'>Distribución de Riesgo de Crédito</div>", unsafe_allow_html=True)
    df_pie = df_credits.groupby('status_es')['total_amount'].sum().reset_index()
    fig_pie = px.pie(df_pie, values='total_amount', names='status_es', hole=0.6, color='status_es', color_discrete_map={'Pagado': '#00e676', 'Activo': '#ffb300', 'Vencido': '#ff5252'})
    fig_pie.update_layout(showlegend=True, legend=dict(font=dict(color="#ffffff"), orientation="h", yanchor="bottom", y=-0.2), margin=dict(l=10, r=10, t=10, b=10), height=280, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_