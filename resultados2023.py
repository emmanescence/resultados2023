import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import zipfile
import io

# Descargar y cargar el archivo CSV con los resultados electorales en fragmentos
zip_url_resultados = 'https://www.argentina.gob.ar/sites/default/files/2023_generales_1.zip'
response = requests.get(zip_url_resultados)
zip_file_resultados = zipfile.ZipFile(io.BytesIO(response.content))

archivo_csv = '2023_Generales/ResultadoElectorales_2023_Generales.csv'

# Cargar y procesar datos en fragmentos
chunk_list = []  # Lista para almacenar fragmentos
with zip_file_resultados.open(archivo_csv) as csv_file:
    for chunk in pd.read_csv(
        csv_file, 
        usecols=['circuito_id', 'cargo_nombre', 'agrupacion_nombre', 'votos_cantidad'],  # Ajusta las columnas necesarias
        dtype={
            'circuito_id': str,
            'cargo_nombre': str,
            'agrupacion_nombre': str,
            'votos_cantidad': 'Int64'  # Especificar como int para ahorrar memoria
        },
        chunksize=5000,  # Tamaño del fragmento
        low_memory=True
    ):
        # Filtrar por 'cargo_nombre' si se necesita reducir aún más la memoria
        chunk_filtered = chunk[chunk['cargo_nombre'] == 'Presidente']  # Ajusta según la selección necesaria
        chunk_list.append(chunk_filtered)

# Concatenar fragmentos para formar el DataFrame completo
csv_df = pd.concat(chunk_list, ignore_index=True)

# Descargar y cargar el archivo GeoJSON con los circuitos electorales
zip_url_circ = 'https://catalogo.datos.gba.gob.ar/dataset/4fe68b69-c788-4c06-ac67-26e4ebc7416b/resource/37bd466c-4a80-4e2e-be11-a68cfe60aa1e/download/circuitos-electorales.zip'
response = requests.get(zip_url_circ)
zip_file_circ = zipfile.ZipFile(io.BytesIO(response.content))

archivo_geojson = 'circuitos-electorales.geojson'

with zip_file_circ.open(archivo_geojson) as geojson_file:
    geo_df = gpd.read_file(geojson_file)

# Crear una función para el mapa y visualizar los datos
def crear_mapa():
    # Ejemplo básico de cómo usar csv_df y geo_df
    # Aquí debes agregar el código específico para unir y visualizar los datos en el mapa
    st.write("Datos cargados correctamente")
    st.write(csv_df.head())
    st.write(geo_df.head())
    # Crear el gráfico o mapa

# Interfaz de Streamlit
st.title('Resultados Electorales y Mapa de Circuitos')
crear_mapa()

