import streamlit as st
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd

st.set_page_config(page_title="Painel de Atendimentos", layout="wide")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "orders" not in st.session_state:
    st.session_state.orders = []

# Login System
st.sidebar.title("Login")
username = st.sidebar.text_input("Usuário:")
password = st.sidebar.text_input("Senha:", type="password")

valid_users = {"admin": "1234", "user": "senha"}

if st.sidebar.button("Entrar"):
    if username in valid_users and valid_users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.sidebar.success("Login realizado!")
    else:
        st.sidebar.error("Usuário ou senha inválidos")

if st.session_state.get("logged_in", False):
    st.sidebar.success(f"Bem-vindo, {st.session_state.username}!")
    if st.sidebar.button("Sair"):
        st.session_state.logged_in = False
        st.rerun()
else:
    st.warning("Por favor, faça login para usar o painel")
    st.stop()

# Main Dashboard
st.title("📊 Painel de Acompanhamento de Atendimentos")

# Tabs
tab1, tab2, tab3 = st.tabs(["Dashboard", "Novo Atendimento", "Gerenciar Pedidos"])

with tab1:
    st.subheader("Resumo de Pedidos")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total de Pedidos", len(st.session_state.orders))
    col2.metric("Pendentes", sum(1 for o in st.session_state.orders if o["status"] == "Pendente"))
    col3.metric("Em Processamento", sum(1 for o in st.session_state.orders if o["status"] == "Processando"))
    col4.metric("Concluídos", sum(1 for o in st.session_state.orders if o["status"] == "Concluído"))
    
    if st.session_state.orders:
        st.subheader("Pedidos Recentes")
        df = pd.DataFrame(st.session_state.orders)
        st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Registrar Novo Atendimento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        order_id = st.text_input("ID do Pedido:")
        client_name = st.text_input("Nome do Cliente:")
    
    with col2:
        service_type = st.selectbox("Tipo de Serviço:", ["Entrega", "Reparo", "Consulta", "Outro"])
        status = st.selectbox("Status:", ["Pendente", "Processando", "Concluído", "Cancelado"])
    
    description = st.text_area("Descrição do Atendimento:")
    priority = st.radio("Prioridade:", ["Baixa", "Média", "Alta"])
    
    if st.button("Registrar Atendimento"):
        if order_id and client_name:
            new_order = {
                "id": order_id,
                "cliente": client_name,
                "tipo": service_type,
                "status": status,
                "prioridade": priority,
                "descricao": description,
                "data": datetime.now().strftime("%d/%m/%Y %H:%M")
            }
            st.session_state.orders.append(new_order)
            st.success("Atendimento registrado com sucesso!")
        else:
            st.error("Preencha ID do Pedido e Nome do Cliente")

with tab3:
    st.subheader("Gerenciar Pedidos")
    
    if st.session_state.orders:
        order_to_manage = st.selectbox("Selecione um pedido:", 
                                       [f"{o['id']} - {o['cliente']}" for o in st.session_state.orders])
        
        selected_idx = [i for i, o in enumerate(st.session_state.orders) 
                       if f"{o['id']} - {o['cliente']}" == order_to_manage][0]
        order = st.session_state.orders[selected_idx]
        
        col1, col2 = st.columns(2)
        with col1:
            new_status = st.selectbox("Atualizar Status:", 
                                     ["Pendente", "Processando", "Concluído", "Cancelado"],
                                     index=["Pendente", "Processando", "Concluído", "Cancelado"].index(order["status"]))
        
        if st.button("Atualizar Pedido"):
            st.session_state.orders[selected_idx]["status"] = new_status
            st.success("Pedido atualizado!")
            st.rerun()
        
        if st.button("Deletar Pedido"):
            st.session_state.orders.pop(selected_idx)
            st.success("Pedido deletado!")
            st.rerun()
    else:
        st.info("Nenhum pedido registrado ainda")