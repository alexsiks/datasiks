import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pytz
import sqlite3

st.set_page_config(layout="wide")

st.title("Geolocalização")

# Configurar banco de dados SQLite
DB_FILE = "geolocation.db"

def init_db():
    """Inicializar banco de dados"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  latitude REAL,
                  longitude REAL,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_location(latitude, longitude, timestamp):
    """Salvar localização no banco de dados"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO locations (latitude, longitude, timestamp) VALUES (?, ?, ?)",
              (latitude, longitude, timestamp))
    conn.commit()
    conn.close()

def get_locations():
    """Recuperar todas as localizações"""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM locations ORDER BY timestamp DESC", conn)
    conn.close()
    return df

# Inicializar banco de dados
init_db()

loc = streamlit_geolocation()

st.write("Sua localização:")
if loc:
    # Obter data/hora em Brasília
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    data_hora_brasilia = datetime.now(tz_brasilia).strftime("%d/%m/%Y %H:%M:%S")
    
    # Salvar localização no banco de dados
    if st.button("Salvar Localização"):
        save_location(loc['latitude'], loc['longitude'], data_hora_brasilia)
        st.success("Localização salva com sucesso!")

    st.write(f"Latitude: {loc['latitude']}")
    st.write(f"Longitude: {loc['longitude']}")
    st.write(f'Data e hora da última atualização: {data_hora_brasilia}')
    


else:
    st.write("Aguardando permissão de geolocalização..")

# Exibir todas as localizações no mapa
st.subheader("Histórico de Localizações")
df_locations = get_locations()

if not df_locations.empty:
    st.dataframe(df_locations)
    
    # Preparar dados para o mapa
    map_data = pd.DataFrame({
        'lat': df_locations['latitude'],
        'lon': df_locations['longitude']
    })
    st.map(map_data, use_container_width=True, zoom=15)
else:
    st.write("Nenhuma localização registrada ainda.")