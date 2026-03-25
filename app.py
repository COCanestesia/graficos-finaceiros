import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# 🔹 Importa funções do seu projeto
from data import carregar_dados
from analise import mostrar_kpis

# ==========================
# CONFIGURAÇÃO DA PÁGINA
# ==========================
st.set_page_config(layout="wide")
st.title("📊 Dashboard Financeiro - Visão Diretoria")

# ==========================
# SELEÇÃO DE MÊS E ANO
# ==========================
mes = st.sidebar.selectbox(
    "Mês", list(range(1, 13)), index=datetime.now().month - 1
)
ano = st.sidebar.number_input(
    "Ano", min_value=2000, max_value=2100, value=datetime.now().year
)

# ==========================
# CARREGAMENTO DE DADOS
# ==========================
df_total = carregar_dados()

# Filtrar apenas dados do mês/ano selecionado
df = df_total[
    (df_total["Data Lançamento"].dt.month == mes) &
    (df_total["Data Lançamento"].dt.year == ano)
]

if df.empty:
    st.warning("Sem dados para esse período")
    st.stop()

# ==========================
# CARREGAMENTO DOS SALDOS (NÃO MOSTRADOS)
# ==========================
def carregar_saldos():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_saldo = conn.read(
        spreadsheet="https://docs.google.com/spreadsheets/d/1VyFBo9qeKQOjdTtvtuQjsVBQGQ54Yh0iYVkaH-iG4wM/edit?usp=sharing",
        worksheet="Saldos"
    )
    df_saldo["Data"] = pd.to_datetime(df_saldo["Data"], dayfirst=True)
    for col in ["Caixa", "Bradesco", "Banco do Brasil"]:
        df_saldo[col] = pd.to_numeric(df_saldo[col], errors="coerce").fillna(0)
    return df_saldo

df_saldo = carregar_saldos()

# Filtrar saldos apenas do mês/ano selecionado
df_saldo_filtrado = df_saldo[
    (df_saldo["Data"].dt.month == mes) &
    (df_saldo["Data"].dt.year == ano)
]

# Somar os saldos do mês para ajustar resultados sem mostrar ao usuário
saldo_total_mes = df_saldo_filtrado[["Caixa", "Bradesco", "Banco do Brasil"]].sum(axis=1).sum()

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

    # 🔹 KPIs - agora usando saldo_total_mes
    mostrar_kpis(df, saldo_inicial=saldo_total_mes)

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

    fig = px.bar(
        df_comp,
        x="Tipo",
        y="Valor",
        color="Tipo",
        color_discrete_map={
            "Receita": "#2ecc71",   # verde
            "Despesa": "#e74c3c"    # vermelho
        }
    )

    fig.update_traces(
        texttemplate="R$ %{y:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )

    fig.update_layout(
        yaxis_tickprefix="R$ ",
        yaxis_title="Valor (R$)"
    )

    st.plotly_chart(fig, use_container_width=True)

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

        fig = px.bar(
            df_rec,
            x="Tipo",
            y="Valor",
            color="Tipo",
            color_discrete_map={
                "Realizado": "#2ecc71",  # verde
                "Projetado": "#3498db"   # azul
            }
        )

        fig.update_traces(
            texttemplate="R$ %{y:,.0f}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
        )

        fig.update_layout(yaxis_tickprefix="R$ ")

        st.plotly_chart(fig, use_container_width=True)

    with colB:
        st.subheader("💸 Despesa")

        despesa_proj = df["Despesa projetada"].sum()

        df_des = pd.DataFrame({
            "Tipo": ["Projetado", "Realizado"],
            "Valor": [despesa_proj, despesa_real]
        })

        fig = px.bar(
            df_des,
            x="Tipo",
            y="Valor",
            color="Tipo",
            color_discrete_map={
                "Realizado": "#e74c3c",  # vermelho
                "Projetado": "#f39c12"   # laranja
            }
        )

        fig.update_traces(
            texttemplate="R$ %{y:,.0f}",
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
        )

        fig.update_layout(yaxis_tickprefix="R$ ")

        st.plotly_chart(fig, use_container_width=True)

    # =========================
    # 📊 ONDE A EMPRESA PERDE DINHEIRO
    # =========================
    st.subheader("📊 Onde a empresa está perdendo dinheiro")

    receita_total = df["Receita realizada"].sum()

    df_cat = df.groupby("Plano de Contas")["Despesa realizada"].sum().reset_index()
    df_cat = df_cat[df_cat["Despesa realizada"] > 0]

    if receita_total > 0:
        df_cat["% Receita"] = df_cat["Despesa realizada"] / receita_total
    else:
        df_cat["% Receita"] = 0

    df_cat = df_cat.sort_values(by="Despesa realizada", ascending=False)

    if not df_cat.empty:
        top1 = df_cat.iloc[0]
        st.error(
            f"🚨 MAIOR GASTO: {top1['Plano de Contas']} "
            f"→ R$ {top1['Despesa realizada']:,.0f} "
            f"({top1['% Receita']:.1%} da receita)"
        )

    fig = px.bar(
        df_cat.head(10),
        x="Plano de Contas",
        y="Despesa realizada",
        color="% Receita",
        color_continuous_scale="Reds",
        text="% Receita"
    )

    fig.update_traces(
        texttemplate="%{text:.1%}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<br>% Receita: %{marker.color:.1%}<extra></extra>"
    )

    fig.update_layout(
        yaxis_tickprefix="R$ ",
        yaxis_title="Valor (R$)"
    )

    st.plotly_chart(fig, use_container_width=True)

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

    total_despesas = df_cat["Despesa realizada"].sum()
    resultado_liquido = receita_real - despesa_real + saldo_total_mes

    col1.metric("Total Despesas", f"R$ {total_despesas:,.0f}")
    col2.metric("% da Receita", f"{(total_despesas / receita_total):.1%}" if receita_total > 0 else "0%")
    col3.metric("Resultado Líquido", f"R$ {resultado_liquido:,.0f}")

    # =========================
    # CONVÊNIOS
    # =========================
    st.subheader("💳 Convênios que mais geram receita")

    df_conv = df[df["Receita realizada"] > 0].groupby("Itens")["Receita realizada"].sum().reset_index()
    df_conv = df_conv.sort_values(by="Receita realizada", ascending=False)

    fig = px.bar(
        df_conv.head(10),
        x="Itens",
        y="Receita realizada"
    )

    fig.update_traces(
        texttemplate="R$ %{y:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )

    fig.update_layout(yaxis_tickprefix="R$ ")

    st.plotly_chart(fig, use_container_width=True)

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
        fig = px.bar(df_group, x=eixo, y=metrica)
    else:
        fig = px.line(df_group, x=eixo, y=metrica)

    fig.update_traces(hovertemplate="<b>%{x}</b><br>Valor: R$ %{y:,.2f}")
    fig.update_layout(yaxis_tickprefix="R$ ")

    st.plotly_chart(fig, use_container_width=True)

# ================================
# 📈 ABA 2 - EVOLUÇÃO
# ================================
with aba2:

    df_evolucao = df_total.copy()

    # Base mensal
    df_evolucao["Mes_dt"] = pd.to_datetime(
        df_evolucao["Data Lançamento"]
    ).dt.to_period("M").dt.to_timestamp()

    df_mes = df_evolucao.groupby("Mes_dt").agg({
        "Receita realizada": "sum",
        "Despesa realizada": "sum"
    }).reset_index().sort_values("Mes_dt")

    # Remover meses zerados
    df_mes = df_mes[
        (df_mes["Receita realizada"] > 0) |
        (df_mes["Despesa realizada"] > 0)
    ]

    # 🔥 NOME DOS MESES EM PT-BR
    meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
        5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
        9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    df_mes["Mes_str"] = df_mes["Mes_dt"].apply(
        lambda x: f"{meses[x.month]}/{x.year}"
    )

    # Acumulados
    df_mes["Receita Acumulada"] = df_mes["Receita realizada"].cumsum()
    df_mes["Despesa Acumulada"] = df_mes["Despesa realizada"].cumsum()

    df_long = df_mes.melt(
        id_vars="Mes_str",
        value_vars=["Receita Acumulada", "Despesa Acumulada"],
        var_name="Tipo",
        value_name="Valor"
    )

    fig = px.line(
        df_long,
        x="Mes_str",
        y="Valor",
        color="Tipo",
        category_orders={"Mes_str": df_mes["Mes_str"].tolist()}
    )

    fig.update_traces(
        hovertemplate="Mês: %{x}<br>Valor: R$ %{y:,.2f}"
    )

    fig.update_layout(
        yaxis=dict(tickprefix="R$ ", title="Valor (R$)")
    )

    st.plotly_chart(fig, use_container_width=True)
    
# ================================
# 📅 ABA 3 - COMPARAÇÃO DE MESES
# ================================
with aba3:

    df_comp = df_total.copy()

    # 🔥 Garantir datetime correto
    df_comp["Mes"] = pd.to_datetime(
        df_comp["Data Lançamento"].dt.to_period("M").dt.to_timestamp()
    )

    df_mes = df_comp.groupby("Mes").agg({
        "Receita realizada": "sum",
        "Despesa realizada": "sum",
        "Receita projetada": "sum",
        "Despesa projetada": "sum"
    }).reset_index().sort_values("Mes")

    # 🔥 Resultado
    df_mes["Resultado"] = df_mes["Receita realizada"] - df_mes["Despesa realizada"]

    # 🔥 Crescimento %
    df_mes["Crescimento Receita (%)"] = (
        df_mes["Receita realizada"].pct_change().fillna(0)
    )

    df_mes["Crescimento Despesa (%)"] = (
        df_mes["Despesa realizada"].pct_change().fillna(0)
    )

    # =========================
    # KPIs
    # =========================
    col1, col2, col3 = st.columns(3)

    df_mes_filtrado = df_mes[
        (df_mes["Receita realizada"] > 0) |
        (df_mes["Despesa realizada"] > 0)
    ]

    if len(df_mes_filtrado) >= 2:
        ultima = df_mes_filtrado.iloc[-1]

        col1.metric(
            "Receita (último mês)",
            f"R$ {ultima['Receita realizada']:,.0f}",
            delta=f"{ultima['Crescimento Receita (%)']:.1%}"
        )

        col2.metric(
            "Despesa (último mês)",
            f"R$ {ultima['Despesa realizada']:,.0f}",
            delta=f"{ultima['Crescimento Despesa (%)']:.1%}",
            delta_color="inverse"
        )

        col3.metric(
            "Resultado",
            f"R$ {ultima['Resultado']:,.0f}"
        )

    # =========================
    # GRÁFICO Receita x Despesa
    # =========================
    df_long = df_mes.melt(
        id_vars="Mes",
        value_vars=["Receita realizada", "Despesa realizada"],
        var_name="Tipo",
        value_name="Valor"
    )

    fig = px.line(
        df_long,
        x="Mes",
        y="Valor",
        color="Tipo"
    )

    # 🔥 Hover corrigido
    fig.update_traces(
        hovertemplate="<b>%{x|%B/%Y}</b><br>Valor: R$ %{y:,.2f}<extra></extra>"
    )

    fig.update_layout(
        yaxis_tickprefix="R$ "
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # GRÁFICO Resultado
    # =========================
    fig = px.bar(
        df_mes,
        x="Mes",
        y="Resultado",
        color="Resultado",
        color_continuous_scale=["#e74c3c", "#2ecc71"],
        text="Resultado"  # 👈 volta o valor no topo
    )

    fig.update_traces(
        texttemplate="R$ %{text:,.0f}",   # 👈 valor formatado
        textposition="outside",
        hovertemplate="<b>%{x|%B/%Y}</b><br>Resultado: R$ %{y:,.2f}<extra></extra>"
    )

    fig.update_layout(
        yaxis_tickprefix="R$ "
    )

    st.plotly_chart(fig, use_container_width=True)

    # =========================
    # TABELA
    # =========================

    # 🔥 Formatar mês/ano (Abril/2026)
    df_mes["Mes"] = pd.to_datetime(df_mes["Mes"]).dt.strftime("%B/%Y")

    st.dataframe(
        df_mes.style.format({
            "Receita realizada": "R$ {:,.2f}",
            "Despesa realizada": "R$ {:,.2f}",
            "Receita projetada": "R$ {:,.2f}",
            "Despesa projetada": "R$ {:,.2f}",
            "Resultado": "R$ {:,.2f}",
            "Crescimento Receita (%)": "{:.1%}",
            "Crescimento Despesa (%)": "{:.1%}"
        }),
        use_container_width=True
    )
