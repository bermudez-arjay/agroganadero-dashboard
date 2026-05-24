import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px

# ==============================================================================
# 1. DESIGN & CORPORATE IDENTITY (UI/UX PREMIUM)
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Gerencial | AgroGanadero",
    page_icon="📊",
    layout="wide",  # Maximiza el uso de espacio en pantallas de oficina
    initial_sidebar_state="expanded"
)

# Inyección de estilos CSS para romper la estética común y dar un acabado de software a medida
st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; padding-bottom: 1.5rem; }
        .metric-card {
            background-color: #fdfdfd;
            border-left: 5px solid #2ecc71;
            padding: 1.2rem;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            border-top: 1px solid #f1f2f6;
            border-right: 1px solid #f1f2f6;
            border-bottom: 1px solid #f1f2f6;
        }
        .metric-card-risk { border-left-color: #e74c3c; }
        h3 { font-weight: 600; color: #2c3e50; font-size: 1.3rem; margin-bottom: 1rem; }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. OPTIMIZED DATA LAYER (PERFORMANCE & SAFE CONNECT)
# ==============================================================================
@st.cache_data(ttl=300) # Mantiene datos en memoria por 5 minutos para proteger el rendimiento de Render
def load_executive_data():
    try:
        db_url = st.secrets["db_credentials"]["connection_string"]
        with psycopg2.connect(db_url) as conn:
            # Traemos columnas explícitas para optimizar el tráfico de red
            sales = pd.read_sql_query("SELECT total_amount, created_at FROM sales WHERE deleted_at IS NULL;", conn)
            credits = pd.read_sql_query("SELECT total_amount, pending_balance, status FROM credits WHERE deleted_at IS NULL;", conn)
            batches = pd.read_sql_query("SELECT code, current_quantity, expiration_date, product_id, state FROM batches WHERE deleted_at IS NULL;", conn)
            customers = pd.read_sql_query("SELECT id FROM customers WHERE deleted_at IS NULL;", conn)
            products = pd.read_sql_query("SELECT id, name FROM products WHERE deleted_at IS NULL;", conn)
        return sales, credits, batches, customers, products
    except Exception as e:
        st.error(f"⚠️ Falla en la comunicación con la infraestructura de Render: {e}")
        return [pd.DataFrame()] * 5

# Carga unificada desde memoria caché
df_sales, df_credits, df_batches, df_customers, df_products = load_executive_data()

# Control de integridad antes de renderizar la interfaz
if df_sales.empty or df_credits.empty:
    st.warning("Conexión exitosa, pero el almacén de datos no registra actividad transaccional o las tablas están vacías.")
    st.stop()

# ==============================================================================
# 3. INTERACTIVE AUDIT FILTERS (GLOBAL SIDEBAR)
# ==============================================================================
st.sidebar.title("🛠️ Filtros de Auditoría")
st.sidebar.markdown("Ajuste los parámetros para recalcular el ecosistema financiero.")

# Preparación del filtro cronológico uniforme
df_sales['fecha'] = pd.to_datetime(df_sales['created_at']).dt.date
min_date, max_date = df_sales['fecha'].min(), df_sales['fecha'].max()

# Input de rango empresarial
date_range = st.sidebar.date_input(
    "Periodo Operativo",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Inyección dinámica de filtros temporales
if len(date_range) == 2:
    df_sales = df_sales[(df_sales['fecha'] >= date_range[0]) & (df_sales['fecha'] <= date_range[1])]

st.sidebar.write("---")
st.sidebar.caption("AgroGanadero v2.0 - Consolidado de Mando Ejecutivo")

# ==============================================================================
# 4. ENCABEZADO INSTITUCIONAL & DATA GOVERNANCE
# ==============================================================================
header_left, header_right = st.columns([4, 1])

with header_left:
    st.title("📊 AgroGanadero | Panel de Control Gerencial")
    st.caption("Consolidado analítico de transacciones, estados de cuentas por cobrar y niveles logísticos de lotes.")

with header_right:
    st.write("")
    # Botón profesional para exportar los datos filtrados directo a un informe de auditoría CSV
    st.download_button(
        label="📥 Exportar Cierre",
        data=df_sales.to_csv(index=False),
        file_name="Cierre_Consolidado_Gerencial.csv",
        mime="text/csv",
        use_container_width=True
    )

st.write("---")

# ==============================================================================
# 5. EXECUTION MATRIX (TARJETAS DE MÉTRICAS / KPIs REESTRUCTURADAS)
# ==============================================================================
kpi_layout = st.columns(4)

with kpi_layout[0]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="💰 Facturación Neto (Efectivo)", value=f"${df_sales['total_amount'].sum():,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_layout[1]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="📈 Créditos Concedidos", value=f"${df_credits['total_amount'].sum():,.2f}")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_layout[2]:
    # Tarjeta con variación de riesgo (Inversa para denotar deuda pendiente en rojo)
    st.markdown('<div class="metric-card metric-card-risk">', unsafe_allow_html=True)
    st.metric(label="⚠️ Riesgo en Calle (Por Cobrar)", value=f"${df_credits['pending_balance'].sum():,.2f}", delta="Acciones de Cobro Requeridas", delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with kpi_layout[3]:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.metric(label="👥 Fincas y Clientes Activos", value=int(df_customers['id'].nunique()))
    st.markdown('</div>', unsafe_allow_html=True)

st.write("##")

# ==============================================================================
# 6. BUSINESS INTEL GRID (REJILLA GRÁFICA COMBINADA)
# ==============================================================================
chart_left, chart_right = st.columns(2)

with chart_left:
    st.markdown("### 📈 Tendencia Macroeconómica de Ventas")
    sales_trend = df_sales.groupby('fecha')['total_amount'].sum().reset_index()
    
    # Cambio profesional de línea simple a Gráfico de Área para ver el volumen real acumulado
    fig_sales = px.area(
        sales_trend, x='fecha', y='total_amount',
        labels={'fecha': 'Cronología de Cierres', 'total_amount': 'Volumen Comercial ($)'},
        template="plotly_white"
    )
    fig_sales.update_traces(line_color='#2ecc71', fillcolor='rgba(46, 204, 113, 0.1)')
    fig_sales.update_layout(margin=dict(l=15, r=15, t=10, b=15), height=320)
    st.plotly_chart(fig_sales, use_container_width=True)

with chart_right:
    st.markdown("### 🍩 Composición y Estado de Riesgo Financiero")
    credit_status = df_credits.groupby('status')['total_amount'].sum().reset_index()
    
    fig_credits = px.pie(
        credit_status, values='total_amount', names='status',
        hole=0.5, template="plotly_white",
        color='status',
        color_discrete_map={'PAID': '#2ecc71', 'ACTIVE': '#f1c40f', 'OVERDUE': '#e74c3c'}
    )
    # Acabado premium: oculta las leyendas repetitivas y mete las etiquetas directo en el gráfico
    fig_credits.update_traces(textinfo='percent+label', marker=dict(bordercolor='#ffffff', width=2))
    fig_credits.update_layout(showlegend=False, margin=dict(l=15, r=15, t=10, b=15), height=320)
    st.plotly_chart(fig_credits, use_container_width=True)

st.write("---")

# ==============================================================================
# 7. LOGISTICS CONTROL BLOCK (INVENTARIOS Y AUDITORÍA DE LOTES)
# ==============================================================================
st.markdown("### 🛡️ Auditoría Operativa de Lotes e Inventario")

ops_left, ops_right = st.columns([2, 3])

with ops_left:
    st.markdown("##### 🚨 Alertas de Vencimiento de Lotes")
    df_batches['expiration_date'] = pd.to_datetime(df_batches['expiration_date'])
    
    # Combinación para extraer los nombres legibles de los productos asociados al lote
    df_prod_batches = df_batches.merge(df_products, left_on='product_id', right_on='id', suffixes=('_lote', '_prod'))
    
    # Filtrado fino y limpio de los 5 lotes más urgentes de atención por vencimiento
    df_alerts = df_prod_batches[['code', 'name', 'current_quantity', 'expiration_date']].sort_values(by='expiration_date').head(5)
    df_alerts['expiration_date'] = df_alerts['expiration_date'].dt.strftime('%d-%m-%Y')
    
    # Cambiamos cabeceras técnicas por nombres comerciales limpios para el gerente
    st.dataframe(
        df_alerts.rename(columns={'code': 'Código Lote', 'name': 'Producto Insumo', 'current_quantity': 'Cant. Disponible', 'expiration_date': 'Vencimiento'}),
        use_container_width=True,
        hide_index=True
    )

with ops_right:
    st.markdown("##### 📦 Distribución de Stock por Lote Específico")
    
    fig_stock = px.bar(
        df_prod_batches.head(12), x='name', y='current_quantity', color='code',
        labels={'name': 'Producto Ganadero / Agrícola', 'current_quantity': 'Unidades en Bodega'},
        template="plotly_white",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_stock.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=240, showlegend=False)
    st.plotly_chart(fig_stock, use_container_width=True)