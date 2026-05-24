import streamlit as st
import psycopg2
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de la Página de Streamlit
st.set_page_config(
    page_title="Dashboard Gerencial - AgroGanadero",
    page_icon="🚜",
    layout="wide"
)

st.title("🚜 Dashboard Gerencial - AgroGanadero")
st.markdown("Análisis financiero, control de inventarios y cartera por cobrar en tiempo real.")
st.write("---")

# 2. Conexión Segura a la Base de Datos PostgreSQL de Render
@st.cache_data(ttl=60) # Cachea los datos por 1 minuto para no saturar Render
def load_data():
    try:
        # Extrae la URL desde los secretos (local o en la nube)
        db_url = st.secrets["db_credentials"]["connection_string"]
        conn = psycopg2.connect(db_url)
        
        # Consultas SQL directas hacia las tablas de Render
        sales = pd.read_sql_query("SELECT * FROM sales;", conn)
        credits = pd.read_sql_query("SELECT * FROM credits;", conn)
        batches = pd.read_sql_query("SELECT * FROM batches;", conn)
        customers = pd.read_sql_query("SELECT * FROM customers;", conn)
        products = pd.read_sql_query("SELECT * FROM products;", conn)
        
        conn.close()
        return sales, credits, batches, customers, products
    except Exception as e:
        st.error(f"Error crítico al conectar con Render: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

# Cargar los DataFrames
df_sales, df_credits, df_batches, df_customers, df_products = load_data()

# Validar que existan datos antes de procesar los gráficos
if not df_sales.empty and not df_credits.empty:

    # ==========================================
    # 3. SECCIÓN DE MÉTRICAS CLAVE (KPIs)
    # ==========================================
    total_sales_revenue = df_sales['total_amount'].sum()
    total_credit_portfolio = df_credits['total_amount'].sum()
    total_pending_balance = df_credits['pending_balance'].sum()
    active_customers_count = df_customers['id'].nunique()

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric(label="💰 Ingresos Totales (Ventas)", value=f"${total_sales_revenue:,.2f}")
    with kpi2:
        st.metric(label="📊 Cartera de Crédito Emitida", value=f"${total_credit_portfolio:,.2f}")
    with kpi3:
        st.metric(label="⚠️ Saldo Pendiente por Cobrar", value=f"${total_pending_balance:,.2f}", delta=f"${total_pending_balance:,.2f}", delta_color="inverse")
    with kpi4:
        st.metric(label="👥 Fincas / Clientes Activos", value=active_customers_count)

    st.write("---")

    # ==========================================
    # 4. FILA DE GRÁFICOS: FINANZAS Y CARTERA
    # ==========================================
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Historial de Ventas")
        # Agrupar ventas por fecha (se asume created_at)
        df_sales['fecha'] = pd.to_datetime(df_sales['created_at']).dt.date
        sales_trend = df_sales.groupby('fecha')['total_amount'].sum().reset_index()
        
        fig_sales = px.line(
            sales_trend, x='fecha', y='total_amount',
            labels={'fecha': 'Fecha', 'total_amount': 'Monto ($)'},
            markers=True, template="plotly_white",
            color_discrete_sequence=['#2ecc71']
        )
        st.plotly_chart(fig_sales, use_container_width=True)

    with col2:
        st.subheader("🍩 Estado Actual de los Créditos")
        # Agrupar créditos por estado (ACTIVE, PAID, OVERDUE)
        credit_status = df_credits.groupby('status')['total_amount'].sum().reset_index()
        
        fig_credits = px.pie(
            credit_status, values='total_amount', names='status',
            hole=0.4, template="plotly_white",
            color='status',
            color_discrete_map={'PAID': '#2ce3a0', 'ACTIVE': '#f1c40f', 'OVERDUE': '#e74c3c'}
        )
        st.plotly_chart(fig_credits, use_container_width=True)

    st.write("---")

    # ==========================================
    # 5. SECCIÓN DE INVENTARIOS Y ALERTAS DE LOTES
    # ==========================================
    st.subheader("🛡️ Control Operativo de Lotes (Batches)")
    
    col_inv1, col_inv2 = st.columns([1, 2])
    
    with col_inv1:
        st.markdown("#### 🚨 Alertas de Lotes Próximos a Vencer")
        # Filtrar lotes ordenados por fecha de vencimiento más cercana
        df_batches['expiration_date'] = pd.to_datetime(df_batches['expiration_date'])
        df_alerts = df_batches[['code', 'current_quantity', 'expiration_date', 'state']].sort_values(by='expiration_date').head(5)
        
        # Formatear fecha para legibilidad
        df_alerts['expiration_date'] = df_alerts['expiration_date'].dt.strftime('%Y-%m-%d')
        st.dataframe(df_alerts, use_container_width=True, hide_index=True)

    with col_inv2:
        st.markdown("#### 📦 Niveles de Stock de Productos por Lote")
        # Cruzar nombres de productos para el gráfico de barras
        df_prod_batches = df_batches.merge(df_products, left_on='product_id', right_on='id', suffixes=('_lote', '_prod'))
        
        fig_stock = px.bar(
            df_prod_batches, x='name', y='current_quantity',
            color='code', barmode='group',
            labels={'name': 'Producto', 'current_quantity': 'Cantidad Disponible en Lote'},
            template="plotly_white"
        )
        st.plotly_chart(fig_stock, use_container_width=True)

else:
    st.warning("Conexión exitosa, pero no se encontraron registros en las tablas analíticas para estructurar el Dashboard.")