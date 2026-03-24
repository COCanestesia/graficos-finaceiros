import altair as alt
import pandas as pd


def limitar_valor(df, coluna):
    df = df.copy()
    limite = df[coluna].quantile(0.95)
    df[coluna] = df[coluna].clip(upper=limite)
    return df


def grafico_receita(df):
    df_plot = df.groupby(df["Data Lançamento"].dt.to_period("M")).agg({
        "Receita realizada": "sum",
        "Receita projetada": "sum"
    }).reset_index()

    df_plot = limitar_valor(df_plot, "Receita projetada")

    df_long = df_plot.melt("Data Lançamento", var_name="Tipo", value_name="Valor")

    return alt.Chart(df_long).mark_bar().encode(
        x="Data Lançamento:N",
        y="Valor:Q",
        color="Tipo"
    )


def grafico_despesa(df):
    df_plot = df.groupby(df["Data Lançamento"].dt.to_period("M")).agg({
        "Despesa realizada": "sum",
        "Despesa projetada": "sum"
    }).reset_index()

    df_long = df_plot.melt("Data Lançamento", var_name="Tipo", value_name="Valor")

    return alt.Chart(df_long).mark_bar().encode(
        x="Data Lançamento:N",
        y="Valor:Q",
        color="Tipo"
    )


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

    chart = alt.Chart(df_cat).mark_bar().encode(
        x="Despesa realizada:Q",
        y=alt.Y("Plano de Contas:N", sort="-x"),
        color="Percentual:Q"
    )

    text = chart.mark_text(align="left", dx=5).encode(
        text=alt.Text("Despesa realizada:Q", format=",.0f")
    )

    return chart + text