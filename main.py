import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

# Separate inputs for day, month, and year
col1, col2, col3 = st.columns(3)

with col1:
    dia = st.number_input("Dia:", min_value=1, max_value=31, step=1)

with col2:
    mes = st.number_input("Mês:", min_value=1, max_value=12, step=1)

with col3:
    ano = st.number_input("Ano:", min_value=1900, max_value=datetime.now().year, step=1)

# Create date from separate inputs
try:
    data_nascimento = datetime(int(ano), int(mes), int(dia)).date()
    
    # Calcular idade corretamente
    hoje = datetime.now().date()
    diferenca = relativedelta(hoje, data_nascimento)
    
    idade = diferenca.years
    meses = diferenca.months
    dias = diferenca.days
    
    if idade >= 18:
        st.write("Você é maior de idade")
    else:
        st.write("Você é menor de idade")
    
    st.write(f"Sua idade: {idade} anos, {meses} meses e {dias} dias")
    
    anos_ate_maioridade = 18 - idade
    
    if anos_ate_maioridade > 0:
        st.write(f"Faltam {anos_ate_maioridade} anos para atingir a maioridade")
    else:
        st.write("Você já atingiu a maioridade")
        
except ValueError:
    st.error("Data inválida. Por favor, verifique os valores inseridos.")