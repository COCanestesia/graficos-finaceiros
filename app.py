import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime

from data import carregar_dados
from analise import mostrar_kpis
from grafico import grafico_receita, grafico_despesa, grafico_categoria

st.set_page_config(layout="wide")
st.title("📊 Dashboard Financeiro - Visão Diretoria")

mes = st.sidebar.selectbox("Mês", list(range(1, 13)), index=datetime.now().month - 1)
ano = st.sidebar.number_input("Ano", value=datetime.now().year)

# 🔥 CARREGA UMA VEZ SÓ
df_total = carregar_dados()

df = df_total[
    (df_total["Data Lançamento"].dt.month == mes) &
    (df_total["Data Lançamento"].dt.year == ano)
]

if df.empty:
    st.warning("Sem dados para esse período")
    st.stop()

# ================================
# ABAS
# ================================
aba1, aba2, aba3 = st.tabs([
    "📊 Visão Geral",
    "📈 Evolução",
    "📅 Comparação de Meses"
])

# ================================
# 📊 ABA 1 - VISÃO GERAL
# ================================
with aba1:
    # 🔥 KPIs
    mostrar_kpis(df)

    st.markdown("---")

    # =========================
    # RECEITA VS DESPESA
    # =========================
    st.subheader("📊 Receita vs Despesa")
    receita_real = df["Receita realizada"].sum()
    despesa_real = df["Despesa realizada"].sum()

    df_comp = pd.DataFrame({
        "Tipo": ["Receita", "Despesa"],
        "Valor": [receita_real, despesa_real]
    })

    st.altair_chart(
        alt.Chart(df_comp).mark_bar(size=80).encode(
            x="Tipo",
            y="Valor",
            color=alt.Color(
                "Tipo",
                scale=alt.Scale(domain=["Receita", "Despesa"], range=["#2ecc71", "#e74c3c"])
            )
        ),
        use_container_width=True
    )

    # =========================
    # PROJETADO VS REAL
    # =========================
    colA, colB = st.columns(2)

    with colA:
        st.subheader("💰 Receita")
        receita_proj = df["Receita projetada"].sum()
        df_rec = pd.DataFrame({
            "Tipo": ["Projetado", "Realizado"],
            "Valor": [receita_proj, receita_real]
        })
        st.altair_chart(
            alt.Chart(df_rec).mark_bar().encode(x="Tipo", y="Valor", color="Tipo"),
            use_container_width=True
        )

    with colB:
        st.subheader("💸 Despesa")
        despesa_proj = df["Despesa projetada"].sum()
        df_des = pd.DataFrame({
            "Tipo": ["Projetado", "Realizado"],
            "Valor": [despesa_proj, despesa_real]
        })
        st.altair_chart(
            alt.Chart(df_des).mark_bar().encode(x="Tipo", y="Valor", color="Tipo"),
            use_container_width=True
        )

    # =========================
    # 📊 ONDE A EMPRESA PERDE DINHEIRO
    # =========================
    st.subheader("📊 Onde a empresa está perdendo dinheiro")

    receita_total = df["Receita realizada"].sum()

    df_cat = (
        df.groupby("Plano de Contas")["Despesa realizada"]
        .sum()
        .reset_index()
    )

    # remover zeros
    df_cat = df_cat[df_cat["Despesa realizada"] > 0]

    # calcular %
    df_cat["% Receita"] = df_cat["Despesa realizada"] / receita_total

    # ordenar
    df_cat = df_cat.sort_values(by="Despesa realizada", ascending=False)

    # =========================
    # 🚨 DIAGNÓSTICO AUTOMÁTICO
    # =========================
    top1 = df_cat.iloc[0]

    st.error(
        f"🚨 MAIOR GASTO: {top1['Plano de Contas']} "
        f"→ R$ {top1['Despesa realizada']:,.0f} "
        f"({top1['% Receita']:.1%} da receita)"
    )

    # =========================
    # 📊 GRÁFICO MELHORADO
    # =========================
    chart = alt.Chart(df_cat.head(10)).mark_bar().encode(
       x=alt.X("Plano de Contas", sort="-y"),
       y=alt.Y("Despesa realizada", title="Valor (R$)"),
       tooltip=[
           "Plano de Contas",
           alt.Tooltip("Despesa realizada", format=",.2f"),
           alt.Tooltip("% Receita", format=".1%")
        ],
       color=alt.condition(
           alt.datum["% Receita"] > 0.3,
           alt.value("#e74c3c"),  # vermelho (crítico)
           alt.value("#3498db")   # azul (normal)
        )
    )

    st.altair_chart(chart, use_container_width=True)


    # =========================
    # 📋 TABELA DETALHADA
    # =========================
    st.subheader("📋 Detalhamento dos gastos")
    st.dataframe(
        df_cat.style.format({
            "Despesa realizada": "R$ {:,.2f}",
            "% Receita": "{:.1%}"
        }),
        use_container_width=True
    )

    # =========================
    # 📉 RESUMO DE IMPACTO
    # =========================
    st.markdown("### 📉 Impacto geral das despesas")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Despesas", f"R$ {df_cat['Despesa realizada'].sum():,.0f}")
    col2.metric("% da Receita", f"{(df_cat['Despesa realizada'].sum()/receita_total):.1%}")
    col3.metric("Categorias críticas (>30%)", f"{(df_cat['% Receita'] > 0.3).sum()}")

    # =========================
    # CONVÊNIOS
    # =========================
    st.subheader("💳 Convênios que mais geram receita")
    df_conv = df[df["Receita realizada"] > 0].groupby("Itens")["Receita realizada"].sum().reset_index()
    df_conv = df_conv.sort_values(by="Receita realizada", ascending=False)
    st.altair_chart(
        alt.Chart(df_conv.head(10)).mark_bar().encode(x=alt.X("Itens", sort="-y"), y="Receita realizada"),
        use_container_width=True
    )

    # =========================
    # 🛠️ DASHBOARD PERSONALIZADO
    # =========================
    st.markdown("---")
    st.subheader("🛠️ Criador de Dashboard")
    eixo = st.selectbox("Eixo X", df.columns)
    metrica = st.selectbox(
        "Métrica",
        ["Receita realizada", "Receita projetada", "Despesa realizada", "Despesa projetada"]
    )
    tipo = st.selectbox("Tipo", ["Barra", "Linha"])
    df_group = df.groupby(eixo)[metrica].sum().reset_index().sort_values(by=metrica, ascending=False)

    if tipo == "Barra":
        chart = alt.Chart(df_group).mark_bar().encode(x=alt.X(eixo, sort="-y"), y=metrica)
    else:
        chart = alt.Chart(df_group).mark_line(point=True).encode(x=eixo, y=metrica)

    st.altair_chart(chart, use_container_width=True)

# ================================
# 📈 ABA 2 - EVOLUÇÃO
# ================================
with aba2:

    df_evolucao = df_total.copy()

    # Transformar Data Lançamento em datetime apenas com mês/ano
    df_evolucao["Mes"] = df_evolucao["Data Lançamento"].dt.to_period("M").dt.to_timestamp()

    df_mes = df_evolucao.groupby("Mes").agg({
        "Receita realizada": "sum",
        "Despesa realizada": "sum"
    }).reset_index()

    # 🔥 remove meses zerados
    df_mes = df_mes[
        (df_mes["Receita realizada"] > 0) |
        (df_mes["Despesa realizada"] > 0)
    ]

    # Calcular acumulado
    df_mes["Receita Acumulada"] = df_mes["Receita realizada"].cumsum()
    df_mes["Despesa Acumulada"] = df_mes["Despesa realizada"].cumsum()

    # Transformar em formato longo
    df_long = df_mes.melt(
        id_vars="Mes",
        value_vars=["Receita Acumulada", "Despesa Acumulada"],
        var_name="Tipo",
        value_name="Valor"
    )

    # Gráfico Altair
    st.altair_chart(
        alt.Chart(df_long).mark_line(point=True).encode(
            x=alt.X("Mes:T", title="Mês", axis=alt.Axis(format="%b/%y")),  # eixo de tempo
            y="Valor:Q",
            color="Tipo:N"
        ),
        use_container_width=True
    )
# ================================
# 📅 ABA 3 - COMPARAÇÃO DE MESES
# ================================
with aba3:

    st.markdown("---")
    st.subheader("📊 Comparação Automática de Meses")
    
    df_comp = df_total.copy()

    # Criar coluna de mês/ano como datetime
    df_comp["Mes_dt"] = pd.to_datetime(df_comp["Data Lançamento"].dt.to_period("M").dt.to_timestamp())

    # Agrupar por mês
    df_mes = (
        df_comp.groupby("Mes_dt")
        .agg({
            "Receita realizada": "sum",
            "Despesa realizada": "sum",
            "Receita projetada": "sum",
            "Despesa projetada": "sum"
        })
        .reset_index()
        .sort_values("Mes_dt")
    )

    # Resultado
    df_mes["Resultado"] = df_mes["Receita realizada"] - df_mes["Despesa realizada"]

    df_mes["Crescimento Receita (%)"] = (
        df_mes["Receita realizada"].pct_change().fillna(0) * 100
    )

    df_mes["Crescimento Despesa (%)"] = (
        df_mes["Despesa realizada"].pct_change().fillna(0) * 100
    )

    # ================================
    # 📊 KPIs DE EVOLUÇÃO
    # ================================
    col1, col2, col3 = st.columns(3)

    df_mes_filtrado = df_mes[
        (df_mes["Receita realizada"] > 0) |
        (df_mes["Despesa realizada"] > 0)
    ]

    if len(df_mes_filtrado) >= 2:
        ultima = df_mes_filtrado.iloc[-1]
        anterior = df_mes_filtrado.iloc[-2]
    
        col1.metric(
            "Receita (último mês)",
            f"R$ {ultima['Receita realizada']:,.0f}",
            delta=f"{ultima['Crescimento Receita (%)']:.1f}%"
        )

        col2.metric(
            "Despesa (último mês)",
            f"R$ {ultima['Despesa realizada']:,.0f}",
            delta=f"{ultima['Crescimento Despesa (%)']:.1f}%",
            delta_color="inverse"
        )

        col3.metric(
            "Resultado",
            f"R$ {ultima['Resultado']:,.0f}"
        )

    # ================================
    # 📈 GRÁFICO RECEITA X DESPESA
    # ================================
    df_long = df_mes.melt(
        id_vars="Mes_dt",
        value_vars=["Receita realizada", "Despesa realizada"],
        var_name="Tipo",
        value_name="Valor"
    )

    chart = alt.Chart(df_long).mark_line(point=True).encode(
        x=alt.X("Mes_dt:T", title="Mês", axis=alt.Axis(format="%b/%y")),
        y=alt.Y("Valor:Q", title="Valor (R$)"),
        color="Tipo",
        tooltip=[alt.Tooltip("Mes_dt:T", title="Mês", format="%b/%Y"),
                 "Tipo",
                 alt.Tooltip("Valor", format=",.2f")]
    ).properties(
        title="📈 Evolução Mensal: Receita x Despesa"
    )

    st.altair_chart(chart, use_container_width=True)

    # ================================
    # 📊 GRÁFICO RESULTADO
    # ================================
    chart_result = alt.Chart(df_mes).mark_bar().encode(
        x=alt.X(
            "Mes_dt:T",
            title="Mês",
            axis=alt.Axis(format="%b/%y")
        ),
        y=alt.Y("Resultado:Q", title="Resultado (R$)"),
        color=alt.condition(
            alt.datum.Resultado > 0,
            alt.value("#2ecc71"),
            alt.value("#e74c3c")
        ),
        tooltip=[
            alt.Tooltip("Mes_dt:T", title="Mês", format="%b/%Y"),
            alt.Tooltip("Resultado:Q", format=",.2f")
        ]
    ).properties(
        title="💰 Resultado Mensal (Lucro / Prejuízo)"
    )

    st.altair_chart(chart_result, use_container_width=True)

    # ================================
    # TABELA DE COMPARAÇÃO
    # ================================
    # formatar para exibição
    df_mes_display = df_mes.copy()
    df_mes_display["Mes"] = df_mes_display["Mes_dt"].dt.strftime("%b/%Y")

    st.dataframe(
        df_mes_display.style.format({
            "Receita realizada": "R$ {:,.2f}",
            "Despesa realizada": "R$ {:,.2f}",
            "Receita projetada": "R$ {:,.2f}",
            "Despesa projetada": "R$ {:,.2f}",
            "Resultado": "R$ {:,.2f}",
            "Crescimento Receita (%)": "{:.1f}%",
            "Crescimento Despesa (%)": "{:.1f}%"
        }),
        use_container_width=True
    )
