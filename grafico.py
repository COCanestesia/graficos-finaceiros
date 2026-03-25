import plotly.express as px
import pandas as pd


def grafico_receita(df):
    df_plot = df.groupby(df["Data Lançamento"].dt.to_period("M")).agg({
        "Receita realizada": "sum",
        "Receita projetada": "sum"
    }).reset_index()

    df_plot["Data Lançamento"] = df_plot["Data Lançamento"].astype(str)

    df_long = df_plot.melt(
        "Data Lançamento",
        var_name="Tipo",
        value_name="Valor"
    )

    fig = px.bar(
        df_long,
        x="Data Lançamento",
        y="Valor",
        color="Tipo",
        barmode="group"
    )

    return fig


def grafico_despesa(df):
    df_plot = df.groupby(df["Data Lançamento"].dt.to_period("M")).agg({
        "Despesa realizada": "sum",
        "Despesa projetada": "sum"
    }).reset_index()

    df_plot["Data Lançamento"] = df_plot["Data Lançamento"].astype(str)

    df_long = df_plot.melt(
        "Data Lançamento",
        var_name="Tipo",
        value_name="Valor"
    )

    fig = px.bar(
        df_long,
        x="Data Lançamento",
        y="Valor",
        color="Tipo",
        barmode="group"
    )

    return fig


def grafico_categoria(df):
    receita_total = df["Receita realizada"].sum()

    df_cat = (
        df.groupby("Plano de Contas")["Despesa realizada"]
        .sum()
        .reset_index()
        .sort_values(by="Despesa realizada", ascending=False)
        .head(7)
    )

    if receita_total > 0:
        df_cat["Percentual"] = df_cat["Despesa realizada"] / receita_total
    else:
        df_cat["Percentual"] = 0

    fig = px.bar(
        df_cat,
        x="Despesa realizada",
        y="Plano de Contas",
        color="Percentual",
        orientation="h",
        color_continuous_scale="Reds"
    )

    return fig
