import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(page_title="Clínica Dani & Gabi", layout="wide", page_icon="🌿")

# --- SISTEMA DE SEGURANÇA (SENHA) ---
def check_password():
    """Retorna True se o utilizador introduziu a senha correta."""
    if "password_correct" not in st.session_state:
        st.subheader("Acesso Restrito")
        senha = st.text_input("Introduza a senha da clínica:", type="password")
        if st.button("Entrar"):
            # DEFINA A SENHA AQUI (Exemplo: clinica2024)
            if senha == "dg@9193": 
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
        return False
    return True

# Se a senha não estiver correta, para a execução aqui
if not check_password():
    st.stop()

# --- INÍCIO DO PROGRAMA APÓS LOGIN ---

# 2. Ligação ao Google Sheets (usa as Secrets que colou no Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    # ttl="0" garante que lemos os dados mais frescos sempre
    return conn.read(worksheet=sheet_name, ttl="0")

st.title("🌿 Gestão de Atendimentos - Dani & Gabi")

# Menu Lateral
aba = st.sidebar.radio("Navegação", ["Painel Financeiro", "Registar Dani", "Registar Gabi", "Registar Gastos"])

# --- LÓGICA DO PAINEL FINANCEIRO (Consolidado) ---
if aba == "Painel Financeiro":
    st.header("📊 Resumo Consolidado (Caixa)")
    
    with st.spinner("A consultar o Google Drive..."):
        df_dani = load_data("Dani")
        df_gabi = load_data("Gabi")
        df_gastos = load_data("Gastos")

    # Cálculos Automáticos
    rec_dani = pd.to_numeric(df_dani[df_dani["Status"] == "Pago"]["Valor"]).sum()
    pend_dani = pd.to_numeric(df_dani[df_dani["Status"] == "Pendente"]["Valor"]).sum()
    
    rec_gabi = pd.to_numeric(df_gabi[df_gabi["Status"] == "Pago"]["Valor"]).sum()
    pend_gabi = pd.to_numeric(df_gabi[df_gabi["Status"] == "Pendente"]["Valor"]).sum()
    
    gas_pagos = pd.to_numeric(df_gastos[df_gastos["Status"] == "Pago"]["Valor"]).sum()
    gas_pend = pd.to_numeric(df_gastos[df_gastos["Status"] == "Pendente"]["Valor"]).sum()

    # Visualização em Cartões (KPIs)
    c1, c2, c3 = st.columns(3)
    c1.metric("Caixa Dani (Pago)", f"R$ {rec_dani:.2f}")
    c2.metric("Caixa Gabi (Pago)", f"R$ {rec_gabi:.2f}")
    c3.metric("Saldo Total Clínica", f"R$ {(rec_dani + rec_gabi) - gas_pagos:.2f}")

    st.divider()
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Pendências a Receber")
        st.write(f"📌 Dani: R$ {pend_dani:.2f}")
        st.write(f"📌 Gabi: R$ {pend_gabi:.2f}")
    with col_b:
        st.subheader("Contas a Pagar")
        st.error(f"💸 Total: R$ {gas_pend:.2f}")

# --- LÓGICA DE REGISTO ---
else:
    nome_aba = "Gastos" if aba == "Registar Gastos" else aba.replace("Registar ", "")
    st.header(f"📝 Novo Registo: {nome_aba}")
    
    df_atual = load_data(nome_aba)

    with st.form("form_registo"):
        data = st.date_input("Data", datetime.now())
        desc = st.text_input("Paciente / Descrição da Despesa")
        valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0)
        pago = st.checkbox("Pago / Recebido?")
        
        if st.form_submit_button("Guardar no Google Drive"):
            nova_linha = pd.DataFrame([{
                "Data": data.strftime("%d/%m/%Y"),
                "Descrição": desc,
                "Valor": valor,
                "Status": "Pago" if pago else "Pendente"
            }])
            df_final = pd.concat([df_atual, nova_linha], ignore_index=True)
            conn.update(worksheet=nome_aba, data=df_final)
            st.success(f"Feito! Dados gravados na aba '{nome_aba}' da sua planilha.")
            st.balloons()
