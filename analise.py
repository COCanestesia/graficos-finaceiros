import streamlit as st

def mostrar_kpis(df):
    receita_real = df["Receita realizada"].sum()
    despesa_real = df["Despesa realizada"].sum()
    resultado = receita_real - despesa_real
    perc = (despesa_real / receita_real * 100) if receita_real > 0 else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Receita", f"R$ {receita_real:,.0f}")
    col2.metric("💸 Despesa", f"R$ {despesa_real:,.0f}")
    col3.metric("📊 Resultado", f"R$ {resultado:,.0f}")
    col4.metric("% Comprometido", f"{perc:.1f}%")

    # Alertas
    if despesa_real > receita_real:
        st.error("🚨 PREJUÍZO: empresa está perdendo dinheiro")
    elif perc > 80:
        st.warning("⚠️ Alto risco financeiro")
    elif perc > 60:
        st.info("ℹ️ Atenção nas despesas")
    else:
        st.success("✅ Situação saudável")