import streamlit as st

def mostrar_kpis(df):
    receita = df["Receita realizada"].sum()
    despesa = df["Despesa realizada"].sum()
    resultado = receita - despesa

    col1, col2, col3 = st.columns(3)

    col1.metric("Receita", f"R$ {receita:,.0f}")
    col2.metric("Despesa", f"R$ {despesa:,.0f}")
    col3.metric("Resultado", f"R$ {resultado:,.0f}")

    if despesa > receita:
        st.error("🚨 PREJUÍZO")
    elif receita > 0 and despesa / receita > 0.8:
        st.warning("⚠️ Alto risco")
    else:
        st.success("✅ Saudável")