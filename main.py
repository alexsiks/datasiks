import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pytz
import sqlite3
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("⛽ Registro de Preços por Localização")

DB_FILE = "geolocation.db"

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

# Tenta capturar localização automaticamente (opcional)
loc = streamlit_geolocation()

lat_auto = loc["latitude"] if loc and loc.get("latitude") else 0.0
lon_auto = loc["longitude"] if loc and loc.get("longitude") else 0.0

with st.form("form_registro"):

    st.markdown("### 📍 Localização")

    latitude = st.number_input(
        "Latitude",
        value=float(lat_auto),
        format="%.6f"
    )

    longitude = st.number_input(
        "Longitude",
        value=float(lon_auto),
        format="%.6f"
    )

    st.markdown("### ⛽ Preços")

    preco_gasolina = st.number_input("Preço Gasolina", min_value=0.0, step=0.01)
    preco_alcool = st.number_input("Preço Álcool", min_value=0.0, step=0.01)
    preco_etanol = st.number_input("Preço Etanol", min_value=0.0, step=0.01)
    diesel = st.number_input("Preço Diesel", min_value=0.0, step=0.01)
    calibragem = st.number_input("Calibragem Pneus", min_value=0.0, step=0.5)

    submit = st.form_submit_button("💾 Salvar Registro")

    if submit:

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
        st.success("Registro salvo com sucesso!")

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
        zoom=12
    )

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "text": """
Data: {data_hora}
Gasolina: R$ {preco_gasolina}
Álcool: R$ {preco_alcool}
Etanol: R$ {preco_etanol}
Diesel: R$ {diesel}
Calibragem: {calibragem}
"""
        }
    ))
else:
    st.info("Nenhum registro ainda.")
