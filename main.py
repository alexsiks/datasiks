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
DB_DIR = os.path.join(BASE_DIR, "dados","raw")
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
        preco_gasolina = st.number_input("Preço Gasolina (R$)", min_value=0.0, step=0.01)
        preco_etanol = st.number_input("Preço Etanol (R$)", min_value=0.0, step=0.01)

    with col2:
        preco_diesel = st.number_input("Preço Diesel (R$)", min_value=0.0, step=0.01)
        valor_calibragem = st.number_input("Valor Calibragem (R$)", min_value=0.0, step=0.50)

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

    # Filtro por data
    min_data = df["data"].min()
    max_data = df["data"].max()

    data_range = st.date_input(
        "Filtrar Período",
        [min_data, max_data],
        min_value=min_data,
        max_value=max_data
    )

    if len(data_range) == 2:
        df = df[(df["data"] >= data_range[0]) & (df["data"] <= data_range[1])]

    # Transformação LONG
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

    tipos = st.multiselect(
        "Filtrar Tipo de Custo",
        df_long["tipo_custo"].unique(),
        default=df_long["tipo_custo"].unique()
    )

    df_filtrado = df_long[df_long["tipo_custo"].isin(tipos)]

    # --------------------------------------------------
    # MAPA + ROSCA
    # --------------------------------------------------
    col_map, col_pie = st.columns([3, 2])

    with col_map:
        fig_map = px.scatter_mapbox(
            df_filtrado,
            lat="latitude",
            lon="longitude",
            color="tipo_custo",
            size="valor",
            size_max=25,
            zoom=12,
            hover_data={
                "tipo_custo": True,
                "valor": ":.2f",
                "data_hora": True
            },
            template="plotly_dark"
        )

        fig_map.update_layout(
            mapbox_style="carto-darkmatter",
            title="🛰 Mapa de Custos",
            margin=dict(l=0, r=0, t=50, b=0)
        )

        st.plotly_chart(fig_map, use_container_width=True)

    with col_pie:

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
            template="plotly_dark"
        )

        fig_pie.update_traces(
            texttemplate="R$ %{value:.2f}",
            textposition="inside"
        )

        fig_pie.update_layout(
            title="💰 Preço Médio por Tipo",
            showlegend=True
        )

        st.plotly_chart(fig_pie, use_container_width=True)

    # --------------------------------------------------
    # BARRAS EMPILHADAS COM VALOR
    # --------------------------------------------------
    st.divider()
    st.subheader("📊 Custos Empilhados por Data")

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
        labels={
            "data": "Data",
            "valor": "Total (R$)",
            "tipo_custo": "Tipo de Custo"
        }
    )

    fig_bar.update_traces(
        texttemplate="R$ %{text:.2f}",
        textposition="inside"
    )

    fig_bar.update_layout(
        title="Total de Custos por Data",
        xaxis_tickangle=-45
    )

    st.plotly_chart(fig_bar, use_container_width=True)

    # --------------------------------------------------
    # MÉTRICAS
    # --------------------------------------------------
    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    for col, tipo, icon in zip(
        [col1, col2, col3, col4],
        ["Gasolina", "Etanol", "Diesel", "Calibragem"],
        ["⛽", "🌱", "🚛", "🛞"]
    ):
        if tipo in tipos:
            media = df_filtrado[df_filtrado["tipo_custo"] == tipo]["valor"].mean()
            col.metric(f"{icon} {tipo}", f"R$ {media:.2f}")
        else:
            col.metric(f"{icon} {tipo}", "-")

    # --------------------------------------------------
    # TABELA
    # --------------------------------------------------
    st.divider()
    st.subheader("📄 Últimos 15 Registros")

    tabela = df.sort_values("data_hora", ascending=False).head(15)
    st.dataframe(tabela, use_container_width=True)

else:
    st.info("Nenhum registro encontrado.")
