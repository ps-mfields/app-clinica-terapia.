import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configurações iniciais do App
st.set_page_config(page_title="Clínica Dani & Gabi", layout="wide", page_icon="🌿")

# Conexão com o Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Função para carregar dados (limpa o cache a cada 10 min para atualizar)
def load_data(sheet_name):
    return conn.read(worksheet=sheet_name, ttl="10m")

st.title("🌿 Gestão de Atendimentos - Dani & Gabi")

# Menu Lateral de Navegação
aba = st.sidebar.radio("Navegação", ["Painel Financeiro", "Registar Dani", "Registar Gabi", "Registar Gastos"])

# --- LÓGICA DO PAINEL FINANCEIRO ---
if aba == "Painel Financeiro":
    st.header("📊 Resumo Consolidado")
    
    with st.spinner("Atualizando dados do Google Drive..."):
        df_dani = load_data("Dani")
        df_gabi = load_data("Gabi")
        df_gastos = load_data("Gastos")

    # Cálculos
    rec_dani = df_dani[df_dani["Status"] == "Pago"]["Valor"].sum()
    pend_dani = df_dani[df_dani["Status"] == "Pendente"]["Valor"].sum()
    
    rec_gabi = df_gabi[df_gabi["Status"] == "Pago"]["Valor"].sum()
    pend_gabi = df_gabi[df_gabi["Status"] == "Pendente"]["Valor"].sum()
    
    gas_pagos = df_gastos[df_gastos["Status"] == "Pago"]["Valor"].sum()
    
    # Exibição
    col1, col2, col3 = st.columns(3)
    col1.metric("Caixa Dani (Recebido)", f"R$ {rec_dani:.2f}")
    col2.metric("Caixa Gabi (Recebido)", f"R$ {rec_gabi:.2f}")
    col3.metric("Saldo Clínica (Líquido)", f"R$ {(rec_dani + rec_gabi) - gas_pagos:.2f}")

    st.divider()
    st.subheader("Pendências a Receber")
    st.write(f"Dani: R$ {pend_dani:.2f} | Gabi: R$ {pend_gabi:.2f}")

# --- LÓGICA DE REGISTO (PARA DANI, GABI OU GASTOS) ---
else:
    # Define qual aba do Google Sheets usar com base no menu
    nome_aba = "Gastos" if aba == "Registar Gastos" else aba.replace("Registar ", "")
    st.header(f"📝 Novo Registo: {nome_aba}")
    
    df_atual = load_data(nome_aba)

    with st.form("registro_form"):
        data = st.date_input("Data", datetime.now())
        desc = st.text_input("Paciente / Descrição")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
        pago = st.checkbox("Pago / Quitado?")
        
        if st.form_submit_button("Guardar no Sistema"):
            nova_linha = pd.DataFrame([{
                "Data": data.strftime("%d/%m/%Y"),
                "Descrição": desc,
                "Valor": valor,
                "Status": "Pago" if pago else "Pendente"
            }])
            df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            conn.update(worksheet=nome_aba, data=df_final)
            st.success(f"Dados enviados para a aba {nome_aba} do Google Drive!")
