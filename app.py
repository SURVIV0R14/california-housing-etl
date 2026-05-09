import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Configuración de la página (Modo Amplio y Título)
st.set_page_config(page_title="California Housing Dashboard", page_icon="🏡", layout="wide")

# Tema Oscuro Personalizado a través de CSS (Opcional para asegurar colores)
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Cargar datos
@st.cache_data
def load_data():
    # Leer el archivo procesado que creamos en el notebook
    df = pd.read_csv("data/processed/housing_clean.csv")
    
    # Reconstruir la columna categórica original para facilitar los filtros visuales
    condiciones = [
        (df['ocean_proximity_<1H OCEAN'] == 1),
        (df['ocean_proximity_INLAND'] == 1),
        (df['ocean_proximity_ISLAND'] == 1),
        (df['ocean_proximity_NEAR BAY'] == 1),
        (df['ocean_proximity_NEAR OCEAN'] == 1)
    ]
    opciones = ['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']
    df['ocean_proximity'] = np.select(condiciones, opciones, default='UNKNOWN')
    
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("No se encontró el archivo de datos. Asegúrate de haber ejecutado el proceso ETL en el Jupyter Notebook para generar 'data/processed/housing_clean.csv'.")
    st.stop()

# 3. Diseño del Dashboard - Encabezado
st.title("🏡 California Housing Analytics")
st.markdown("Exploración interactiva del mercado inmobiliario en California. Descubre cómo la ubicación y los ingresos afectan el precio de las viviendas.")

st.info("💡 **Nota Importante:** Los precios mostrados (desde $14,999) corresponden a los datos del Censo de Estados Unidos del año **1990**. Esta es la razón por la cual los valores inmobiliarios son mucho más bajos que los precios del mercado actual.")

# 4. Barra Lateral (Sidebar) para Filtros
st.sidebar.image("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=300&auto=format&fit=crop", caption="California Real Estate")
st.sidebar.header("🔍 Filtros de Búsqueda")

# Filtro de precio (Slider de Rango)
price_range = st.sidebar.slider("Rango de Precio ($)", 
                              min_value=int(df['median_house_value'].min()), 
                              max_value=int(df['median_house_value'].max()), 
                              value=(int(df['median_house_value'].min()), int(df['median_house_value'].max())), 
                              step=10000)

# Filtro de ubicación (Multiselect)
ocean_options = df['ocean_proximity'].unique().tolist()
selected_ocean = st.sidebar.multiselect("Proximidad al Océano", options=ocean_options, default=ocean_options)

# Aplicar filtros al DataFrame
df_filtered = df[(df['median_house_value'] >= price_range[0]) & 
                 (df['median_house_value'] <= price_range[1]) & 
                 (df['ocean_proximity'].isin(selected_ocean))]

# 5. KPIs (Métricas Principales)
st.markdown("### 📊 Métricas Generales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Distritos Encontrados", f"{len(df_filtered):,}")
col2.metric("Precio Promedio", f"${df_filtered['median_house_value'].mean():,.0f}")
col3.metric("Ingreso Promedio", f"${df_filtered['median_income'].mean() * 10000:,.0f}")
col4.metric("Edad Promedio Casa", f"{df_filtered['housing_median_age'].mean():.1f} años")

st.markdown("---")

# 6. Visualizaciones de Alto Impacto con Plotly
col_map, col_chart = st.columns([3, 2])

with col_map:
    st.subheader("📍 Distribución Geográfica de Precios")
    st.markdown("El tamaño de la burbuja representa la **población**.")
    # Mapa scatter mapbox con tema oscuro
    fig_map = px.scatter_mapbox(df_filtered, 
                                lat="latitude", 
                                lon="longitude", 
                                color="median_house_value",
                                size="population",
                                color_continuous_scale=px.colors.sequential.Plasma, # Colores vibrantes sobre fondo oscuro
                                size_max=15, 
                                zoom=4.8,
                                mapbox_style="carto-darkmatter", # Mapa oscuro!
                                hover_name="ocean_proximity")
    
    # Hacer el fondo transparente para acoplarse al tema de Streamlit
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)", font_color="white")
    st.plotly_chart(fig_map, use_container_width=True)

with col_chart:
    st.subheader("📈 Relación entre Ingresos y Precios")
    st.markdown("<p style='font-size: 14px; color: #a0a0a0;'>Este gráfico demuestra la fuerte relación positiva entre el poder adquisitivo de un distrito y el valor de sus propiedades. Cada punto representa un distrito entero; nota cómo la tendencia sube: a mayor ingreso, casas más caras.</p>", unsafe_allow_html=True)
    
    # Gráfico de dispersión
    fig_scatter = px.scatter(df_filtered, 
                             x="median_income", 
                             y="median_house_value", 
                             color="median_house_value",
                             color_continuous_scale=px.colors.sequential.Plasma,
                             template="plotly_dark", # Tema oscuro de plotly
                             opacity=0.6,
                             labels={"median_income": "Ingreso Promedio Anual (x $10,000 USD)", 
                                     "median_house_value": "Precio Promedio de la Casa ($)"})
    fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin={"t":10})
    st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")
st.caption("Desarrollado por Giancarlo Stevens usando Python, Pandas y Streamlit para mi Portafolio de GitHub.")
