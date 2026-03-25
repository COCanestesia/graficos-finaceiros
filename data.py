import pandas as pd
import streamlit as st

# Link direto para export CSV da aba do Google Sheets
URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTI1XmAnbQk_zwRZbWjfIlugdZScvM3j_TybcHl-g5Ib4mdfPTOio3Z45yNVVCQGQ5eXQI0iG_fH_-0/pub?gid=2000195997&single=true&output=csv"


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


@st.cache_data(ttl=300)
def carregar_dados():
    # 🔹 Lê direto do CSV publicado
    df = pd.read_csv(URL)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
    )

    df["valor_final"] = df["Valor"].apply(limpar_valor)

    df = df[df["valor_final"] < 50_000_000]

    df["Data Lançamento"] = pd.to_datetime(
        df["Data Lançamento"], dayfirst=True, errors="coerce"
    ).dt.normalize()

    df["Data de Pagamento"] = pd.to_datetime(
        df["Data de Pagamento"], dayfirst=True, errors="coerce"
    ).dt.normalize()

    df = df.dropna(subset=["Data Lançamento"])

    df["Classificação"] = df["Classificação"].fillna("").str.lower()
    df["Plano de Contas"] = df["Plano de Contas"].fillna("")
    df["Itens"] = df["Itens"].fillna("")

    df["Semana"] = df["Data Lançamento"].apply(categorizar_semana)

    # RECEITA
    df["Receita projetada"] = df.apply(
        lambda x: x["valor_final"] if "receita" in x["Classificação"] else 0,
        axis=1,
    )

    df["Receita realizada"] = df.apply(
        lambda x: x["valor_final"]
        if "receita" in x["Classificação"] and pd.notna(x["Data de Pagamento"])
        else 0,
        axis=1,
    )

    # DESPESA
    df["Despesa projetada"] = df.apply(
        lambda x: x["valor_final"] if "receita" not in x["Classificação"] else 0,
        axis=1,
    )

    df["Despesa realizada"] = df.apply(
        lambda x: x["valor_final"]
        if "receita" not in x["Classificação"] and pd.notna(x["Data de Pagamento"])
        else 0,
        axis=1,
    )

    # 🔥 CORREÇÃO (ÚNICA ADIÇÃO)
    colunas_valor = [
        "Receita realizada",
        "Despesa realizada",
        "Receita projetada",
        "Despesa projetada"
    ]

    for col in colunas_valor:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    return df
