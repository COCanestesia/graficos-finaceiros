import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

URL = "https://docs.google.com/spreadsheets/d/1VyFBo9qeKQOjdTtvtuQjsVBQGQ54Yh0iYVkaH-iG4wM/edit"
ABA = "Planejamento Financeiro Mensal"


def limpar_valor(valor):
    try:
        if pd.isna(valor):
            return 0.0

        if isinstance(valor, (int, float)):
            return float(valor)

        valor = str(valor)
        valor = valor.replace("R$", "").strip()
        valor = valor.replace(".", "")
        valor = valor.replace(",", ".")

        return float(valor)
    except:
        return 0.0


def categorizar_semana(data):
    if pd.isna(data):
        return "Sem Data"

    dia = data.day

    if dia <= 7:
        return "Semana 1"
    elif dia <= 14:
        return "Semana 2"
    elif dia <= 21:
        return "Semana 3"
    else:
        return "Semana 4"


# 🔥 CACHE AQUI (RESOLVE LIMITE)
@st.cache_data(ttl=300)
def carregar_dados():

    conn = st.connection("gsheets", type=GSheetsConnection)

    df = conn.read(
        spreadsheet=URL,
        worksheet=ABA
    )

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
    )

    df["valor_final"] = df["Valor"].apply(limpar_valor)

    df = df[df["valor_final"] < 50_000_000]

    # ⬅ Garantir que Data Lançamento e Data de Pagamento sejam datetime normalizados
    df["Data Lançamento"] = pd.to_datetime(
        df["Data Lançamento"],
        dayfirst=True,
        errors="coerce"
    ).dt.normalize()

    df["Data de Pagamento"] = pd.to_datetime(
        df["Data de Pagamento"],
        dayfirst=True,
        errors="coerce"
    ).dt.normalize()

    df = df.dropna(subset=["Data Lançamento"])

    df["Classificação"] = df["Classificação"].fillna("").str.lower()
    df["Plano de Contas"] = df["Plano de Contas"].fillna("")
    df["Itens"] = df["Itens"].fillna("")

    df["Semana"] = df["Data Lançamento"].apply(categorizar_semana)

    # RECEITA
    df["Receita projetada"] = df.apply(
        lambda x: x["valor_final"]
        if "receita" in x["Classificação"]
        else 0,
        axis=1,
    )

    df["Receita realizada"] = df.apply(
        lambda x: x["valor_final"]
        if "receita" in x["Classificação"]
        and pd.notna(x["Data de Pagamento"])
        else 0,
        axis=1,
    )

    # DESPESA
    df["Despesa projetada"] = df.apply(
        lambda x: x["valor_final"]
        if "receita" not in x["Classificação"]
        else 0,
        axis=1,
    )

    df["Despesa realizada"] = df.apply(
        lambda x: x["valor_final"]
        if "receita" not in x["Classificação"]
        and pd.notna(x["Data de Pagamento"])
        else 0,
        axis=1,
    )

    return df
        else 0,
        axis=1,
    )

    return df
