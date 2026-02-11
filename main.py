import streamlit as st


idade=int(input("Insira a sua Idade:"))

if idade >= 18:
    st.write("Você é maior de idade")
else:
    st.write("Você é menor de idade")

anos_ate_maioridade = 18 - idade
st.write(f"Faltam {anos_ate_maioridade} anos para atingir a maioridade")