import streamlit as st
import pandas as pd
import requests
import zipfile
import io
import geopandas as gpd

# Función para cargar el GeoJSON desde un ZIP
def load_geojson_from_zip(zip_url, geojson_filename):
    response = requests.get(zip_url)
    zip_file = zipfile.ZipFile(io.BytesIO(response.content))
    with zip_file.open(geojson_filename) as geojson_file:
        return gpd.read_file(geojson_file)

# URL del archivo comprimido y nombre del archivo GeoJSON dentro del ZIP
zip_url_circ = 'https://catalogo.datos.gba.gob.ar/dataset/4fe68b69-c788-4c06-ac67-26e4ebc7416b/resource/37bd466c-4a80-4e2e-be11-a68cfe60aa1e/download/circuitos-electorales.zip'
archivo_geojson = 'circuitos-electorales.geojson'

# Cargar el archivo GeoJSON y filtrar las columnas necesarias
geo_data = load_geojson_from_zip(zip_url_circ, archivo_geojson)
geo_data = geo_data[['circuito', 'cabecera', 'geometry']]

# Eliminar los ceros a la izquierda en la columna 'circuito'
geo_data['circuito'] = geo_data['circuito'].astype(str).str.lstrip('0')

# Realizar el merge con la tabla de resultados
merged_df = pd.merge(csv_df, geo_data, how='left', left_on='circuito_id', right_on='circuito')

# Agrupar por agrupacion_nombre y sumar votos_cantidad
df_resultado = merged_df.groupby(['agrupacion_nombre', 'cabecera'])['votos_cantidad'].sum().reset_index()

# Calcular el total de votos y los porcentajes
total_votos = df_resultado['votos_cantidad'].sum()
df_resultado['porcentaje'] = (df_resultado['votos_cantidad'] / total_votos) * 100

# Asignar colores según la agrupación política
colores = {
    'JUNTOS POR EL CAMBIO': 'yellow',
    'LA LIBERTAD AVANZA': 'purple',
    'UNION POR LA PATRIA': 'blue',
    'Otros': 'red'
}

# Mapear colores a las agrupaciones
df_resultado['color'] = df_resultado['agrupacion_nombre'].map(colores).fillna('red')

# Mostrar la tabla resultante
st.write(f'**Resultados para el Cargo: {cargo_seleccionado} y Circuito ID: {circuito_seleccionado}**')
st.dataframe(df_resultado)

# Crear gráfico con Altair
chart = alt.Chart(df_resultado).mark_bar().encode(
    x=alt.X('agrupacion_nombre:N', title='Agrupación'),
    y=alt.Y('porcentaje:Q', title='Porcentaje de Votos'),
    color=alt.Color('color:N', scale=None, legend=None)  # Usar los colores asignados
).properties(
    width=600,
    height=400,
    title=f'Resultados Electorales en {circuito_seleccionado}'
)

# Mostrar el gráfico
st.altair_chart(chart)

