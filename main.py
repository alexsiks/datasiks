import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pytz
import sqlite3
import os
import plotly.express as px

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
st.subheader("📊 Análise Executiva")

df = get_registros()

if not df.empty:

    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df["data"] = df["data_hora"].dt.date

    # Transformação para formato longo
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

    tipos = st.multiselect(
        "Filtrar Tipo de Custo",
        df_long["tipo_custo"].unique(),
        default=df_long["tipo_custo"].unique()
    )

    df_filtrado = df_long[df_long["tipo_custo"].isin(tipos)]

    # --------------------------------------------------
    # MAPA (CORRIGIDO)
    # --------------------------------------------------
    st.subheader("🛰 Mapa de Custos")

    if not df_filtrado.empty:

        centro_lat = df_filtrado["latitude"].mean()
        centro_lon = df_filtrado["longitude"].mean()

        fig_map = px.scatter_mapbox(
            df_filtrado,
            lat="latitude",
            lon="longitude",
            color="tipo_custo",
            size="valor",
            size_max=30,
            zoom=12,
            center={"lat": centro_lat, "lon": centro_lon},
            hover_name="tipo_custo",
            hover_data={
                "valor": ":.2f",
                "data_hora": True,
                "latitude": False,
                "longitude": False
            },
            color_discrete_map=cores,
            template="plotly_dark"
        )

        # ❌ REMOVIDO marker.line (causava erro)

        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            margin=dict(l=0, r=0, t=40, b=0),
            legend_title="Tipo de Custo",
            title="Distribuição Geográfica dos Custos"
        )

        st.plotly_chart(fig_map, use_container_width=True)

    else:
        st.info("Nenhum dado para exibir no mapa.")

    # --------------------------------------------------
    # GRÁFICO ROSCA (MÉDIA)
    # --------------------------------------------------
    st.subheader("💰 Preço Médio por Tipo")

    resumo_media = (
        df_filtrado.groupby("tipo_custo")["valor"]
        .mean()
        .reset_index()
    )

    fig_pie = px.pie(
        resumo_media,
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

    fig_pie.update_layout(
        title="Preço Médio por Tipo de Custo"
    )

    st.plotly_chart(fig_pie, use_container_width=True)

    # --------------------------------------------------
    # BARRAS EMPILHADAS POR DATA
    # --------------------------------------------------
    st.subheader("📊 Custos por Data")

    agrupado = (
        df_filtrado.groupby(["data", "tipo_custo"])["valor"]
        .sum()
        .reset_index()
    )

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

    fig_bar.update_layout(
        xaxis_tickangle=-45,
        title="Total de Custos por Data"
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # --------------------------------------------------
    # TABELA
    # --------------------------------------------------
    st.subheader("📄 Últimos 15 Registros")

    tabela = df.sort_values("data_hora", ascending=False).head(15)

    st.dataframe(tabela, use_container_width=True)

else:
    st.info("Nenhum registro encontrado.")
