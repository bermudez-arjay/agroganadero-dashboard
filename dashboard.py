import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Configuración mejorada
def apply_custom_styles():
    st.markdown("""
        <style>
            .stApp { background-color: #0b0f19; }
            .metric-card { 
                background: linear-gradient(145deg, #161c2e, #111625);
                padding: 20px; border-radius: 12px; border: 1px solid #2a3558;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            }
            .chart-container { 
                background-color: #161c2e; padding: 15px; border-radius: 10px;
                border: 1px solid #1f2a4a; margin-bottom: 20px;
            }
            h3 { color: #e0e0e0 !important; font-size: 1.1rem !important; margin-bottom: 15px !important; }
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- GRÁFICO CIRCULAR MEJORADO ---
# Usamos colores más vibrantes
st.subheader("Distribución de Riesgo")
fig_pie = px.pie(df_credit_risk, values='amount', names='status', hole=0.7,
                 color='status',
                 color_discrete_map={'PENDING': '#3498db', 'PAID': '#2ecc71', 'OVERDUE': '#e74c3c'})
fig_pie.update_layout(showlegend=True, paper_bgcolor='rgba(0,0,0,0)', font_color='white', margin=dict(t=0, b=0, l=0, r=0))
st.plotly_chart(fig_pie, use_container_width=True)

# --- TENDENCIA (Más estilizada) ---
st.subheader("Tendencia de Ventas")
fig_bar = px.bar(sales_trend, x='date', y='amount', text_auto='.2s')
fig_bar.update_traces(marker_color='#3498db', marker_line_width=0)
fig_bar.update_layout(template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_bar, use_container_width=True)

# --- STOCK POR LOTE (Stack mejorado) ---
st.subheader("Stock por Producto y Lote")
fig_stock = px.bar(df_stock, x='productName', y='currentQuantity', color='batchCode', 
                   barmode='stack', template="plotly_dark")
fig_stock.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
st.plotly_chart(fig_stock, use_container_width=True)
