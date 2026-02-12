import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import sqlite3
import pydeck as pdk
import requests

st.set_page_config(layout="wide")
st.title("⛽ Registro Automático de Localização por IP")

DB_FILE = "geolocation.db"

# -----------------------------
# FUNÇÃO GEO IP
# -----------------------------
def get_location_by_ip():
    try:
        response = requests.get("http://ip-api.com/json/")
        data = response.json()
        return data["lat"], data["lon"]
    except:
        return -14.2350, -51.9253  # fallback centro do Brasil

# -----------------------------
# BANCO
# -----------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            data_hora TEXT,
            preco_gasolina REAL,
            preco_alcool REAL,
            preco_etanol REAL,
            diesel REAL,
            calibragem REAL
        )
    ''')
    conn.commit()
    conn.close()

def save_registro(dados):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO registros 
        (latitude, longitude, data_hora, preco_gasolina, preco_alcool, 
         preco_etanol, diesel, calibragem)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, dados)
    conn.commit()
    conn.close()

def get_registros():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query(
        "SELECT * FROM registros ORDER BY id DESC",
        conn
    )
    conn.close()
    return df

init_db()

# -----------------------------
# FORMULÁRIO
# -----------------------------
st.subheader("⛽ Registrar Preços")

with st.form("form_registro"):

    preco_gasolina = st.number_input("Preço Gasolina", min_value=0.0, step=0.01)
    preco_alcool = st.number_input("Preço Álcool", min_value=0.0, step=0.01)
    preco_etanol = st.number_input("Preço Etanol", min_value=0.0, step=0.01)
    diesel = st.number_input("Preço Diesel", min_value=0.0, step=0.01)
    calibragem = st.number_input("Calibragem Pneus", min_value=0.0, step=0.5)

    submit = st.form_submit_button("Salvar Registro")

    if submit:

        # Captura automática via IP (sem permissão)
        latitude, longitude = get_location_by_ip()

        tz = pytz.timezone("America/Sao_Paulo")
        data_hora = datetime.now(tz).strftime("%d/%m/%Y %H:%M:%S")

        dados = (
            latitude,
            longitude,
            data_hora,
            preco_gasolina,
            preco_alcool,
            preco_etanol,
            diesel,
            calibragem
        )

        save_registro(dados)
        st.success("Registro salvo automaticamente com localização por IP!")

# -----------------------------
# HISTÓRICO
# -----------------------------
st.subheader("📊 Histórico")

df = get_registros()

if not df.empty:
    st.dataframe(df, use_container_width=True)

# -----------------------------
# MAPA
# -----------------------------
st.subheader("🗺 Mapa")

if not df.empty:

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position='[longitude, latitude]',
        get_radius=120,
        get_fill_color=[0, 150, 255, 160],
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=df.iloc[0]["latitude"],
        longitude=df.iloc[0]["longitude"],
        zoom=10
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state],
        tooltip={"text": "Data: {data_hora}\nGasolina: R$ {preco_gasolina}"}
    ))

else:
    st.info("Nenhum registro ainda.")
