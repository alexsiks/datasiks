import streamlit as st
from datetime import datetime, timedelta


idade = st.number_input("Digite sua idade:", min_value=0, max_value=120, step=1)

if idade >= 18:
    st.write("Você é maior de idade")
else:
    st.write("Você é menor de idade")

# Calcular data de nascimento
hoje = datetime.now()
data_nascimento = hoje - timedelta(days=idade*365)
st.write(f"Sua data de nascimento aproximada: {data_nascimento.strftime('%d/%m/%Y')}")

anos_ate_maioridade = 18 - idade

if anos_ate_maioridade >= 0:
    st.write(f"Faltam {anos_ate_maioridade} anos para atingir a maioridade")
else:
    st.write("Você já atingiu a maioridade")