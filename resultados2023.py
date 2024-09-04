import streamlit as st
import pandas as pd
import requests
import zipfile
import io
import geopandas as gpd
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Función para descargar y leer el archivo CSV desde un ZIP
@st.cache_data
def load_csv_from_zip(zip_url, csv_filename):
    response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    with zip_file.open(csv_filename) as csv_file:
        return pd.read_csv(csv_file, usecols=['distrito_nombre', 'circuito_id', 'cargo_nombre', 'agrupacion_nombre', 'votos_cantidad'], low_memory=False)

# Función para descargar y leer el archivo GeoJSON desde un ZIP
@st.cache_data
def load_geojson_from_zip(zip_url, geojson_filename):
    response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    with zip_file.open(geojson_filename) as geojson_file:
        return gpd.read_file(geojson_file)

# URLs y nombres de archivos
zip_url_resultados = 'https://www.argentina.gob.ar/sites/default/files/2023_generales_1.zip'
csv_filename = '2023_Generales/ResultadoElectorales_2023_Generales.csv'
zip_url_circ = 'https://catalogo.datos.gba.gob.ar/dataset/4fe68b69-c788-4c06-ac67-26e4ebc7416b/resource/37bd466c-4a80-4e2e-be11-a68cfe60aa1e/download/circuitos-electorales.zip'
archivo_geojson = 'circuitos-electorales.geojson'

# Cargar los datos
csv_df = load_csv_from_zip(zip_url_resultados, csv_filename)
geo_data = load_geojson_from_zip(zip_url_circ, archivo_geojson)

# Convertir la columna 'circuito_id' a cadena y quitar ceros a la izquierda
csv_df['circuito_id'] = csv_df['circuito_id'].astype(str).str.lstrip('0')

# Filtrar por Provincia de Buenos Aires
csv_df = csv_df[csv_df['distrito_nombre'] == 'Provincia de Buenos Aires']

# Agregar columna con porcentaje de votos
csv_df['votos_total'] = csv_df.groupby('circuito_id')['votos_cantidad'].transform('sum')
csv_df['votos_porcentaje'] = (csv_df['votos_cantidad'] / csv_df['votos_total']) * 100

# Configuración de Streamlit
st.title('Resultados Electorales con Mapa')

# Selección de la cabecera
st.sidebar.header('Seleccionar Cabecera')
header_options = geo_data['departamen'].unique()
selected_header = st.sidebar.selectbox('Elige una cabecera', header_options)

# Agregar un selectbox para seleccionar el cargo
cargos = csv_df['cargo_nombre'].unique()
cargo_seleccionado = st.sidebar.selectbox('Selecciona un Cargo:', cargos)

# Filtrar los datos según el cargo seleccionado
df_filtrado = csv_df[csv_df['cargo_nombre'] == cargo_seleccionado]

# Agregar un selectbox para seleccionar el circuito_id
circuitos = df_filtrado['circuito_id'].unique()
circuito_seleccionado = st.sidebar.selectbox('Selecciona un Circuito ID:', circuitos)

# Filtrar los datos según el circuito seleccionado
df_filtrado = df_filtrado[df_filtrado['circuito_id'] == circuito_seleccionado]

# Agrupar por agrupacion_nombre y sumar votos_cantidad
df_resultado = df_filtrado.groupby('agrupacion_nombre')['votos_cantidad'].sum().reset_index()

# Mostrar la tabla resultante
st.write(f'**Resultados para el Cargo: {cargo_seleccionado} y Circuito ID: {circuito_seleccionado}**')
st.dataframe(df_resultado)

# Filtrar los datos del GeoDataFrame
filtered_geo_data = geo_data[geo_data['departamen'] == selected_header]

# Unir los datos filtrados con el GeoDataFrame
geo_data_combined = filtered_geo_data.merge(df_filtrado[['circuito_id', 'votos_porcentaje']], left_on='circuito_id', right_on='circuito_id', how='left')

# Determinar el color según la agrupación con más votos
def get_color(agrupacion_nombre):
    if agrupacion_nombre == 'JUNTOS POR EL CAMBIO':
        return 'yellow'
    elif agrupacion_nombre == 'LA LIBERTAD AVANZA':
        return 'violet'
    elif agrupacion_nombre == 'UNION POR LA PATRIA':
        return 'blue'
    else:
        return 'grey'

# Agregar columna de color al GeoDataFrame
geo_data_combined['color'] = geo_data_combined['agrupacion_nombre'].apply(get_color)

# Mostrar mapa
fig, ax = plt.subplots(figsize=(12, 10))
divider = make_axes_locatable(ax)
cax = divider.append_axes("right", size="5%", pad=0.1)

# Graficar el mapa
geo_data_combined.plot(ax=ax, color=geo_data_combined['color'], edgecolor='black')
ax.set_title(f'Circuitos Electorales para {selected_header}', fontsize=16)
ax.set_xlabel('Longitud', fontsize=12)
ax.set_ylabel('Latitud', fontsize=12)

# Mostrar el mapa en Streamlit
st.pyplot(fig)

