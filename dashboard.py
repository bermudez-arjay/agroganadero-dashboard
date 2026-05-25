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
    initial_sidebar_state="auto"
)

# Inyección de estilos CSS para clonar la interfaz ejecutiva
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
# 2. CAPA DE CONEXIÓN OPTIMIZADA A POSTGRESQL (RENDER)
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
    st.error("Almacén de datos vacío o inaccesible. Verifique los credenciales en secrets.toml.")
    st.stop()

# Procesamiento de fechas
df_sales['fecha'] = pd.to_datetime(df_sales['created_at']).dt.date
sales_trend = df_sales.groupby('fecha')['total_amount'].sum().reset_index().sort_values('fecha')

# ==============================================================================
# 3. CONSTRUCCIÓN DE LA INTERFAZ EJECUTIVA
# ==============================================================================

# --- ENCABEZADO SUPERIOR ---
header_col1, header_col2 = st.columns([3, 1])
with header_col1:
    st.markdown("<h2 style='margin:0;'>Dashboard Gerencial</h2>", unsafe_allow_html=True)
with header_col2:
    st.write("")
    st.download_button("📥 EXPORTAR DATA AUDIT", data=df_sales.to_csv(index=False), file_name="Data_Audit.csv", mime="text/csv", use_container_width=True)

st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)

# --- FILA 1: KPIs FINANCIEROS ---
kpi_cols = st.columns([1, 1, 1, 1])

with kpi_cols[0]:
    total_rev = df_sales['total_amount'].sum()
    st.markdown(f"""
        <div class="executive-container" style="margin-bottom: 0px; border-bottom-left-radius: 0px; border-bottom-right-radius: 0px;">
            <div class="section-title">Ingresos Totales (Ventas)</div>
            <div class="main-metric">C${total_rev:,.2f}</div>
            <div class="metric-delta delta-positive">▲ En Crecimiento Operativo</div>
        </div>
    """, unsafe_allow_html=True)
    fig_spark1 = go.Figure(go.Scatter(x=sales_trend['fecha'], y=sales_trend['total_amount'], mode='lines', fill='tozeroy', line=dict(color='#00e676', width=1.5), fillcolor='rgba(0, 230, 118, 0.08)'))
    fig_spark1.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False), margin=dict(l=10, r=10, t=0, b=5), height=35, paper_bgcolor='#1e2640', plot_bgcolor='#1e2640')
    st.plotly_chart(fig_spark1, use_container_width=True, config={'displayModeBar': False})

with kpi_cols[1]:
    total_cred = df_credits['total_amount'].sum()
    st.markdown(f"""
        <div class="executive-container" style="height: 182px;">
            <div class="section-title">Cartera Concedida</div>
            <div class="main-metric">C${total_cred:,.2f}</div>
            <div class="metric-delta delta-positive" style="color: #00b0ff;">● Línea de Crédito Activa</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_cols[2]:
    total_pending = df_credits['pending_balance'].sum()
    st.markdown(f"""
        <div class="executive-container" style="height: 182px; border-left: 4px solid #ff5252;">
            <div class="section-title">Riesgo en Calle (Por Cobrar)</div>
            <div class="main-metric" style="color: #ff5252;">C${total_pending:,.2f}</div>
            <div class="metric-delta delta-negative">⚠️ Gestión de Cobro Requerida</div>
        </div>
    """, unsafe_allow_html=True)

with kpi_cols[3]:
    total_cust = df_customers['id'].nunique()
    st.markdown(f"""
        <div class="executive-container" style="height: 182px;">
            <div class="section-title">Clientes Activos</div>
            <div class="main-metric" style="color: #e040fb;">{total_cust}</div>
            <div class="metric-delta">👥</div>
        </div>
    """, unsafe_allow_html=True)

# --- FILA 2: DISTRIBUCIÓN & TENDENCIA ---
row2_col1, row2_col2, row2_col3 = st.columns([1, 1.5, 1])

with row2_col1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Distribución de Riesgo de Crédito</div>", unsafe_allow_html=True)
    credit_status = df_credits.groupby('status')['total_amount'].sum().reset_index()
    fig_pie = px.pie(credit_status, values='total_amount', names='status', hole=0.6, color='status', color_discrete_map={'PAID': '#00e676', 'ACTIVE': '#ffb300', 'OVERDUE': '#ff5252'})
    fig_pie.update_layout(showlegend=True, legend=dict(font=dict(color="#ffffff"), orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5), margin=dict(l=10, r=10, t=10, b=10), height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Tendencia Cierre de Ventas Temporales</div>", unsafe_allow_html=True)
    fig_trend = px.bar(sales_trend, x='fecha', y='total_amount')
    fig_trend.update_traces(marker_color='#00b0ff')
    fig_trend.add_scatter(x=sales_trend['fecha'], y=sales_trend['total_amount'], mode='lines+markers', name='Tendencia', line=dict(color='#00e676', width=2.5))
    fig_trend.update_layout(showlegend=False, xaxis=dict(title='', showgrid=False, tickfont=dict(color='#8fa0dd')), yaxis=dict(title='', showgrid=True, gridcolor='#2a3558', tickfont=dict(color='#8fa0dd')), margin=dict(l=10, r=10, t=10, b=10), height=280, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

with row2_col3:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Índice de Salud Financiera</div>", unsafe_allow_html=True)
    recovery_rate = (1 - (total_pending / total_cred)) * 100 if total_cred > 0 else 100
    fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=recovery_rate, number={'suffix': "%", 'font': {'color': '#ffffff', 'size': 35}}, gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#00e676"}, 'steps': [{'range': [0, 50], 'color': '#ff5252'}, {'range': [50, 80], 'color': '#ffb300'}, {'range': [80, 100], 'color': '#00e676'}]}))
    fig_gauge.update_layout(margin=dict(l=20, r=20, t=30, b=10), height=260, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_gauge, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)

# --- FILA 3: AUDITORÍA CRÍTICA ---
row3_col1, row3_col2 = st.columns([1.2, 1.8])

with row3_col1:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🚨 Alertas Críticas de Vencimiento de Lotes</div>", unsafe_allow_html=True)
    df_batches['expiration_date'] = pd.to_datetime(df_batches['expiration_date'])
    df_prod_batches = df_batches.merge(df_products, left_on='product_id', right_on='id', suffixes=('_lote', '_prod'))
    df_alerts = df_prod_batches[['code', 'name', 'current_quantity', 'expiration_date']].sort_values(by='expiration_date').head(5)
    df_alerts['expiration_date'] = df_alerts['expiration_date'].dt.strftime('%d-%m-%Y')
    st.dataframe(df_alerts.rename(columns={'code': 'Lote', 'name': 'Insumo', 'current_quantity': 'Cant.', 'expiration_date': 'Vencimiento'}), use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with row3_col2:
    st.markdown("<div class='executive-container'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📦 Niveles de Stock de Productos por Lote Activo</div>", unsafe_allow_html=True)
    safe_palette = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
    fig_stock = px.bar(df_prod_batches.head(15), x='name', y='current_quantity', color='code', color_discrete_sequence=safe_palette)
    fig_stock.update_layout(showlegend=False, xaxis=dict(title='', tickfont=dict(color='#8fa0dd', size=10)), yaxis=dict(title='', showgrid=True, gridcolor='#2a3558', tickfont=dict(color='#8fa0dd')), margin=dict(l=10, r=10, t=10, b=10), height=215, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_stock, use_container_width=True, config={'displayModeBar': False})
    st.markdown("</div>", unsafe_allow_html=True)