import streamlit as st
from datetime import datetime


data_nascimento = st.date_input("Digite sua data de nascimento:")

# Calcular idade
hoje = datetime.now().date()
idade = (hoje - data_nascimento).days // 365

if idade >= 18:
    st.write("Você é maior de idade")
else:
    st.write("Você é menor de idade")

st.write(f"Sua idade: {idade} anos")

anos_ate_maioridade = 18 - idade

if anos_ate_maioridade > 0:
    st.write(f"Faltam {anos_ate_maioridade} anos para atingir a maioridade")
else:
    st.write("Você já atingiu a maioridade")