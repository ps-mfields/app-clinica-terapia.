import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Clínica Dani & Gabi", layout="centered")
st.title("🏥 Controle Financeiro - Dani & Gabi")

# Conexão com a planilha (usando os Secrets que você já colou)
conn = st.connection("gsheets", type=GSheetsConnection)

# Formulário de Lançamento
with st.form("fluxo_caixa"):
    usuario = st.selectbox("Profissional", ["Dani", "Gabi"])
    data = st.date_input("Data")
    categoria = st.selectbox("Categoria", ["Sessão", "Avaliação", "Aluguel", "Material", "Outros"])
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    tipo = st.radio("Tipo", ["Entrada", "Saída"])
    
    enviar = st.form_submit_button("Registrar Lançamento")

if enviar:
    # Cria o novo dado
    novo_lancamento = pd.DataFrame([{
        "Data": data.strftime("%d/%m/%Y"),
        "Categoria": categoria,
        "Descrição": descricao,
        "Valor": valor,
        "Tipo": tipo
    }])
    
    # Busca os dados existentes na aba da profissional
    dados_atuais = conn.read(worksheet=usuario)
    
    # Junta o novo dado aos antigos
    dados_atualizados = pd.concat([dados_atuais, novo_lancamento], ignore_index=True)
    
    # Salva de volta na aba correta
    conn.update(worksheet=usuario, data=dados_atualizados)
    st.success(f"Lançamento de {usuario} registrado com sucesso!")
