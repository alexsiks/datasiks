import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pytz
import sqlite3

# --------------------------------------------------
# CONFIGURAÇÃO STREAMLIT
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("⛽ Preço Médio de Combustível por Localização")

# --------------------------------------------------
# BANCO DE DADOS
# --------------------------------------------------
DB_FILE = "geolocation.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            timestamp TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_location(latitude, longitude, timestamp):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute(
        "INSERT INTO locations (latitude, longitude, timestamp) VALUES (?, ?, ?)",
        (latitude, longitude, timestamp)
    )

    conn.commit()
    conn.close()


def get_locations():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM locations ORDER BY id DESC",
        conn
    )
    conn.close()
    return df


# Inicializar banco
init_db()

# --------------------------------------------------
# BOTÃO PARA PERMITIR LOCALIZAÇÃO
# --------------------------------------------------
st.subheader("📍 Capturar Localização")

if st.button("📍 Capturar Localização Atual"):
    if "latitude" not in st.session_state:
        st.session_state.latitude = None
        st.session_state.longitude = None


        
        loc = streamlit_geolocation()

        if loc and loc.get("latitude") and loc.get("longitude"):

            st.session_state.latitude = loc["latitude"]
            st.session_state.longitude = loc["longitude"]

            tz_brasilia = pytz.timezone("America/Sao_Paulo")
            data_hora_brasilia = datetime.now(tz_brasilia).strftime("%d/%m/%Y %H:%M:%S")

            save_location(
                st.session_state.latitude,
                st.session_state.longitude,
                data_hora_brasilia
            )

            st.success("Localização capturada e salva com sucesso!")


# Mostrar localização atual
if st.session_state.latitude and st.session_state.longitude:
    st.info(
        f"Latitude: {st.session_state.latitude:.6f} | "
        f"Longitude: {st.session_state.longitude:.6f}"
    )

# --------------------------------------------------
# HISTÓRICO
# --------------------------------------------------
st.subheader("📊 Histórico de Localizações")

df_locations = get_locations()

if not df_locations.empty:

    st.dataframe(df_locations, use_container_width=True)

    # Preparar dados para mapa
    map_data = pd.DataFrame({
        "lat": df_locations["latitude"],
        "lon": df_locations["longitude"]
    })

    st.map(map_data, use_container_width=True, zoom=12)

else:
    st.info("Nenhuma localização registrada ainda.")
