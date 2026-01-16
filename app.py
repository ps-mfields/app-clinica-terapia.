# app.py
import streamlit as st
import pandas as pd
from datetime import date
from st_gsheets_connection import GSheetsConnection

st.set_page_config(page_title="Controle Financeiro - Clínica", layout="centered")

st.title("💰 Controle Financeiro da Clínica")

# Conexão com Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Seletor de profissional
profissional = st.selectbox(
    "Selecione a profissional",
    ["Dani", "Gabi"]
)

# Categorias pré-definidas (ajuste se quiser)
CATEGORIAS = [
    "Consulta",
    "Procedimento",
    "Aluguel",
    "Material",
    "Impostos",
    "Outros"
]

with st.form("form_financeiro"):
    data = st.date_input("Data", value=date.today())
    categoria = st.selectbox("Categoria", CATEGORIAS)
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.0, step=0.01)
    tipo = st.radio("Tipo", ["Entrada", "Saída"])

    submitted = st.form_submit_button("Salvar")

if submitted:
    novo_registro = pd.DataFrame(
        [{
            "Data": data.strftime("%Y-%m-%d"),
            "Categoria": categoria,
            "Descrição": descricao,
            "Valor": valor,
            "Tipo": tipo
        }]
    )

    conn.append(
        worksheet=profissional,
        df=novo_registro
    )

    st.success(f"Registro salvo com sucesso para {profissional}!")
