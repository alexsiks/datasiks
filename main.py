import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pytz
import sqlite3
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("📍 Geolocalização com Histórico no Mapa")

DB_FILE = "geolocation.db"

# -----------------------------
# BANCO DE DADOS
# -----------------------------
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

init_db()

# -----------------------------
# GEOLOCALIZAÇÃO ATUAL
# -----------------------------
st.subheader("📌 Sua localização atual")

loc = streamlit_geolocation()

latitude_atual = None
longitude_atual = None

if loc and loc.get("latitude") and loc.get("longitude"):

    tz_brasilia = pytz.timezone("America/Sao_Paulo")
    data_hora = datetime.now(tz_brasilia).strftime("%d/%m/%Y %H:%M:%S")

    latitude_atual = loc["latitude"]
    longitude_atual = loc["longitude"]

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Latitude", f"{latitude_atual:.6f}")
        st.metric("Longitude", f"{longitude_atual:.6f}")

    with col2:
        st.write(f"🕒 Atualizado em: {data_hora}")

        if st.button("Salvar Localização"):
            save_location(latitude_atual, longitude_atual, data_hora)
            st.success("Localização salva com sucesso!")

else:
    st.info("Aguardando permissão de geolocalização...")

# -----------------------------
# HISTÓRICO
# -----------------------------
st.subheader("🗂 Histórico de Localizações")

df_locations = get_locations()

if not df_locations.empty:
    st.dataframe(df_locations, use_container_width=True)

# -----------------------------
# MAPA COM GEOLOCALIZAÇÃO + HISTÓRICO
# -----------------------------
st.subheader("🗺 Mapa de Localizações")

layers = []

# Camada histórico (azul)
if not df_locations.empty:
    layer_historico = pdk.Layer(
        "ScatterplotLayer",
        data=df_locations,
        get_position='[longitude, latitude]',
        get_radius=80,
        get_fill_color=[0, 0, 255, 160],
        pickable=True,
    )
    layers.append(layer_historico)

# Camada localização atual (vermelho)
if latitude_atual and longitude_atual:
    df_atual = pd.DataFrame({
        "latitude": [latitude_atual],
        "longitude": [longitude_atual]
    })

    layer_atual = pdk.Layer(
        "ScatterplotLayer",
        data=df_atual,
        get_position='[longitude, latitude]',
        get_radius=120,
        get_fill_color=[255, 0, 0, 200],
        pickable=True,
    )
    layers.append(layer_atual)

# Definir centro do mapa
if latitude_atual and longitude_atual:
    view_state = pdk.ViewState(
        latitude=latitude_atual,
        longitude=longitude_atual,
        zoom=13,
        pitch=0
    )
elif not df_locations.empty:
    view_state = pdk.ViewState(
        latitude=df_locations.iloc[0]["latitude"],
        longitude=df_locations.iloc[0]["longitude"],
        zoom=13,
        pitch=0
    )
else:
    view_state = pdk.ViewState(
        latitude=-14.2350,  # Centro do Brasil
        longitude=-51.9253,
        zoom=4,
        pitch=0
    )

st.pydeck_chart(pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    tooltip={"text": "Latitude: {latitude}\nLongitude: {longitude}"}
))
