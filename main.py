import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pytz
import sqlite3
import os
import plotly.express as px
import numpy as np
from math import radians, sin, cos, sqrt, atan2

# --------------------------------------------------
# CONFIGURAÇÃO STREAMLIT
# --------------------------------------------------
st.set_page_config(
    page_title="Dashboard Custos Automotivos",
    layout="wide"
)

st.title("🚗 Dashboard Executivo de Custos Automotivos")

# --------------------------------------------------
# CONFIGURAÇÃO BANCO
# --------------------------------------------------
BASE_DIR = os.getcwd()
DB_DIR = os.path.join(BASE_DIR, "dados", "raw")
os.makedirs(DB_DIR, exist_ok=True)

DB_FILE = os.path.join(DB_DIR, "custos.db")


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL,
            longitude REAL,
            data_hora TEXT,
            preco_gasolina REAL,
            preco_etanol REAL,
            preco_diesel REAL,
            valor_calibragem REAL
        )
    """)

    conn.commit()
    conn.close()


def save_registro(dados):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO registros (
            latitude,
            longitude,
            data_hora,
            preco_gasolina,
            preco_etanol,
            preco_diesel,
            valor_calibragem
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
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


# --------------------------------------------------
# FUNÇÃO HAVERSINE (DISTÂNCIA KM)
# --------------------------------------------------
def calcular_distancia(lat1, lon1, lat2, lon2):
    R = 6371  # raio da Terra em km

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    return R * c


init_db()

# --------------------------------------------------
# FORMULÁRIO
# --------------------------------------------------
st.subheader("📍 Registrar Novo Custo")

loc = streamlit_geolocation()

with st.form("form_registro"):

    col1, col2 = st.columns(2)

    with col1:
        preco_gasolina = st.number_input("Preço Gasolina (R$)", 0.0, step=0.01)
        preco_etanol = st.number_input("Preço Etanol (R$)", 0.0, step=0.01)

    with col2:
        preco_diesel = st.number_input("Preço Diesel (R$)", 0.0, step=0.01)
        valor_calibragem = st.number_input("Valor Calibragem (R$)", 0.0, step=0.50)

    submit = st.form_submit_button("💾 Salvar Registro")

    if submit:
        if loc and loc.get("latitude") and loc.get("longitude"):

            tz = pytz.timezone("America/Sao_Paulo")
            agora = datetime.now(tz)

            dados = (
                loc["latitude"],
                loc["longitude"],
                agora.strftime("%Y-%m-%d %H:%M:%S"),
                preco_gasolina,
                preco_etanol,
                preco_diesel,
                valor_calibragem
            )

            save_registro(dados)
            st.success("Registro salvo com sucesso!")

        else:
            st.warning("Permita o acesso à localização no navegador.")

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
st.divider()
st.subheader("📊 Filtros")

df = get_registros()

if not df.empty:

    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df["data"] = df["data_hora"].dt.date

    # --------------------------------------------------
    # FILTRO DE DATA
    # --------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        data_inicial = st.date_input(
            "Data Inicial",
            value=df["data"].min()
        )

    with col2:
        data_final = st.date_input(
            "Data Final",
            value=df["data"].max()
        )

    df = df[(df["data"] >= data_inicial) & (df["data"] <= data_final)]

    # --------------------------------------------------
    # FILTRO DE RAIO
    # --------------------------------------------------
    st.subheader("📍 Filtro por Localização")

    raio_km = st.slider("Raio em KM", 1, 100, 10)

    usar_localizacao = st.checkbox("Usar minha localização como centro")

    if usar_localizacao and loc and loc.get("latitude"):

        lat_user = loc["latitude"]
        lon_user = loc["longitude"]

        df["distancia_km"] = df.apply(
            lambda row: calcular_distancia(
                lat_user,
                lon_user,
                row["latitude"],
                row["longitude"]
            ),
            axis=1
        )

        df = df[df["distancia_km"] <= raio_km]

        st.success(f"Filtrando registros em até {raio_km} km")

    # --------------------------------------------------
    # TRANSFORMAÇÃO LONG
    # --------------------------------------------------
    df_long = df.melt(
        id_vars=["id", "latitude", "longitude", "data_hora", "data"],
        value_vars=[
            "preco_gasolina",
            "preco_etanol",
            "preco_diesel",
            "valor_calibragem"
        ],
        var_name="tipo_custo",
        value_name="valor"
    )

    df_long = df_long[df_long["valor"] > 0]

    nomes = {
        "preco_gasolina": "Gasolina",
        "preco_etanol": "Etanol",
        "preco_diesel": "Diesel",
        "valor_calibragem": "Calibragem"
    }

    df_long["tipo_custo"] = df_long["tipo_custo"].map(nomes)

    cores = {
        "Gasolina": "#ff4b4b",
        "Etanol": "#00cc96",
        "Diesel": "#636efa",
        "Calibragem": "#ffa600"
    }

    # --------------------------------------------------
    # MAPA
    # --------------------------------------------------
    st.subheader("🛰 Mapa de Custos")

    if not df_long.empty:

        centro_lat = df_long["latitude"].mean()
        centro_lon = df_long["longitude"].mean()

        fig_map = px.scatter_mapbox(
            df_long,
            lat="latitude",
            lon="longitude",
            color="tipo_custo",
            size="valor",
            size_max=30,
            zoom=12,
            center={"lat": centro_lat, "lon": centro_lon},
            hover_data={
                "valor": ":.2f",
                "data_hora": True
            },
            color_discrete_map=cores,
            template="plotly_dark"
        )

        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin=dict(l=0, r=0, t=40, b=0),
            legend_title="Tipo de Custo"
        )

        st.plotly_chart(fig_map, use_container_width=True)

    # --------------------------------------------------
    # GRÁFICO ROSCA MÉDIA
    # --------------------------------------------------
    st.subheader("💰 Preço Médio por Tipo")

    resumo = df_long.groupby("tipo_custo")["valor"].mean().reset_index()

    fig_pie = px.pie(
        resumo,
        names="tipo_custo",
        values="valor",
        hole=0.6,
        template="plotly_dark",
        color="tipo_custo",
        color_discrete_map=cores
    )

    fig_pie.update_traces(
        texttemplate="R$ %{value:.2f}",
        textposition="inside"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    # --------------------------------------------------
    # BARRAS EMPILHADAS
    # --------------------------------------------------
    st.subheader("📊 Custos por Data")

    agrupado = df_long.groupby(["data", "tipo_custo"])["valor"].sum().reset_index()

    fig_bar = px.bar(
        agrupado,
        x="data",
        y="valor",
        color="tipo_custo",
        barmode="stack",
        template="plotly_dark",
        text="valor",
        color_discrete_map=cores
    )

    fig_bar.update_traces(
        texttemplate="R$ %{text:.2f}",
        textposition="inside"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # --------------------------------------------------
    # TABELA
    # --------------------------------------------------
    st.subheader("📄 Últimos 15 Registros")

    st.dataframe(df.sort_values("data_hora", ascending=False).head(15),
                 use_container_width=True)

else:
    st.info("Nenhum registro encontrado.")
