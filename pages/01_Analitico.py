import streamlit as st
import pandas as pd
import plotly.express as px
from utils import fetch_production_data

# Configuración de página
st.set_page_config(page_title="Dashboard Analítico", layout="wide")

# Estilos ejecutivos oscuros (coherentes con el dashboard principal)
st.markdown("""
    <style>
        .stApp { background-color: #111625; }
        h1, h2, h3 { color: #ffffff !important; }
        .metric-card { 
            background-color: #1e2640; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #2a3558; 
            margin-bottom: 10px;
        }
        /* Forzar visibilidad del botón de menú */
        [data-testid="stSidebarCollapseButton"] { visibility: visible !important; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Análisis Profundo de Operaciones")

# Carga de datos
df_sales, df_credits, df_batches, df_customers, df_products = fetch_production_data()

# --- FILTROS ---
st.sidebar.header("Filtros de Análisis")
if not df_products.empty:
    selected_product = st.sidebar.selectbox("Seleccionar Insumo:", df_products['name'].unique())

    # Lógica de filtrado con manejo de seguridad
    prod_row = df_products[df_products['name'] == selected_product]
    
    if not prod_row.empty:
        prod_id = prod_row.iloc[0]['id']
        selling_price = prod_row.iloc[0].get('selling_price', 0)
        purchase_price = prod_row.iloc[0].get('purchase_price', 0)
        
        prod_batches = df_batches[df_batches['product_id'] == prod_id]
        total_stock = prod_batches['current_quantity'].sum()

        # --- FILA 1: KPIs DE PRODUCTO ---
        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Stock Actual", f"{total_stock} Unidades")
        col2.metric("Lotes Activos", len(prod_batches))
        col3.metric("Precio de Venta", f"C${selling_price:,.2f}")
        col4.metric("Valor Inv. (Costo)", f"C${(total_stock * purchase_price):,.2f}")

        st.markdown("---")

        # --- FILA 2: GRÁFICOS ---
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            st.subheader("Distribución de Cantidades por Lote")
            fig_bar = px.bar(prod_batches, x='code', y='current_quantity', color='code', 
                             template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_bar.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)

        with row2_col2:
            st.subheader("Cronograma de Vencimiento")
            if 'expiration_date' in prod_batches.columns:
                prod_batches['expiration_date'] = pd.to_datetime(prod_batches['expiration_date'])
                fig_scatter = px.scatter(prod_batches, x='expiration_date', y='current_quantity', 
                                         size='current_quantity', color='code', 
                                         template="plotly_dark", color_discrete_sequence=['#00e676'])
                fig_scatter.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_scatter, use_container_width=True)

        # --- FILA 3: TABLA ---
        st.subheader("Detalle de Lotes")
        st.dataframe(prod_batches.rename(columns={
            'code': 'Lote', 
            'current_quantity': 'Stock', 
            'expiration_date': 'Vencimiento',
            'state': 'Estado'
        }), use_container_width=True, hide_index=True)
        
    else:
        st.error("Producto no encontrado.")
else:
    st.warning("No hay productos cargados en la base de datos.")