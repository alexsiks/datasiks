import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.title("Calculadora de Idade.")

# Separate inputs for day, month, and year.
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

    # Simple login system
    st.sidebar.title("Login")

    username = st.sidebar.text_input("Usuário:")
    password = st.sidebar.text_input("Senha:", type="password")

    # Hardcoded credentials (replace with secure authentication in production)
    valid_users = {"admin": "1234", "user": "senha"}

    if st.sidebar.button("Entrar"):
        if username in valid_users and valid_users[username] == password:
            st.session_state.logged_in = True
            st.sidebar.success("Login realizado!")
        else:
            st.sidebar.error("Usuário ou senha inválidos")

    if st.session_state.get("logged_in", False):
        st.sidebar.success(f"Bem-vindo, {username}!")
        if st.sidebar.button("Sair"):
            st.session_state.logged_in = False
    else:
        st.warning("Por favor, faça login para usar a calculadora")
        st.stop()