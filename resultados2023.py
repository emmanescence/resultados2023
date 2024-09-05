import streamlit as st
import geopandas as gpd
import pandas as pd
import requests
import zipfile
import io
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Función para descargar y leer el archivo GeoJSON desde un ZIP
@st.cache_resource
def load_geojson_from_zip(zip_url, geojson_filename):
    response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    with zip_file.open(geojson_filename) as geojson_file:
        return gpd.read_file(geojson_file)

# URL del archivo comprimido y nombre del archivo GeoJSON dentro del ZIP
zip_url_circ = 'https://catalogo.datos.gba.gob.ar/dataset/4fe68b69-c788-4c06-ac67-26e4ebc7416b/resource/37bd466c-4a80-4e2e-be11-a68cfe60aa1e/download/circuitos-electorales.zip'
archivo_geojson = 'circuitos-electorales.geojson'

# Cargar el archivo GeoJSON
geo_data = load_geojson_from_zip(zip_url_circ, archivo_geojson)

# Cargar el archivo CSV con datos adicionales
# URL del archivo comprimido
zip_url_resultados = 'https://www.argentina.gob.ar/sites/default/files/2023_generales_1.zip'

# Descargar el archivo ZIP
response = requests.get(zip_url_resultados)
zip_file_resultados = zipfile.ZipFile(io.BytesIO(response.content))

# Listar los archivos dentro del ZIP
archivo_csv = '2023_Generales/ResultadoElectorales_2023_Generales.csv'

# Leer el archivo CSV en chunks
chunksize = 10**6  # Ajusta este tamaño según la capacidad de memoria disponible
chunks = []
for chunk in pd.read_csv(zip_file_resultados.open(archivo_csv), usecols=['distrito_nombre', 'circuito_id', 'cargo_nombre', 'agrupacion_nombre', 'votos_cantidad'], chunksize=chunksize, low_memory=False):
    # Filtrar cada chunk
    chunk_filtered = chunk[chunk['distrito_nombre'] == 'Buenos Aires']
    chunks.append(chunk_filtered)

# Concatenar todos los chunks
csv_df = pd.concat(chunks, ignore_index=True)

# Eliminar un cero a la izquierda en circuito_id
csv_df['circuito_id'] = csv_df['circuito_id'].astype(str).str.lstrip('0')

# Asegurarse de que ambas columnas sean del mismo tipo de dato
geo_data['circuito'] = geo_data['circuito'].astype(str)
csv_data['circuito_id'] = csv_data['circuito_id'].astype(str)

# Realizar el merge entre el GeoDataFrame y el DataFrame
merged_data = geo_data.merge(csv_data, left_on='circuito', right_on='circuito_id')

# Configuración de Streamlit
st.title('Mapa de Circuitos Electorales con Datos Adicionales')

# Selección de la cabecera
st.sidebar.header('Seleccionar Cabecera')
header_options = merged_data['departamen'].unique()
selected_header = st.sidebar.selectbox('Elige una cabecera', header_options)

# Opción para colorear por un atributo
atributos = ['poblacion', 'area', 'otros_atributos']  # Ejemplo de atributos, ajusta según tus datos
atributo_seleccionado = st.sidebar.selectbox('Colorear por:', atributos)

# Mostrar mapa para la cabecera seleccionada
if st.sidebar.button('Mostrar Mapa para la Cabecera Seleccionada'):
    # Filtrar los datos del GeoDataFrame
    filtered_geo_data = merged_data[merged_data['departamen'] == selected_header]
    
    fig, ax = plt.subplots(figsize=(10, 10))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    
    # Graficar el mapa coloreado por el atributo seleccionado
    filtered_geo_data.plot(column=atributo_seleccionado, ax=ax, legend=True, cmap='viridis', edgecolor='black')
    ax.set_title(f'Circuitos Electorales para {selected_header}', fontsize=16)
    ax.set_xlabel('Longitud', fontsize=12)
    ax.set_ylabel('Latitud', fontsize=12)
    
    st.pyplot(fig)

# Mostrar todos los circuitos con sus cabeceras
if st.sidebar.checkbox('Ver Todos los Circuitos con Sus Cabeceras'):
    fig, ax = plt.subplots(figsize=(10, 10))
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    
    # Graficar todos los circuitos coloreados por el atributo seleccionado
    merged_data.plot(column=atributo_seleccionado, ax=ax, legend=True, cmap='viridis', edgecolor='black')
    ax.set_title('Todos los Circuitos Electorales', fontsize=16)
    ax.set_xlabel('Longitud', fontsize=12)
    ax.set_ylabel('Latitud', fontsize=12)
    
    st.pyplot(fig)
