import streamlit as st

def mostrar_kpis(df, saldo_inicial=0):
    receita_real = df["Receita realizada"].sum()
    despesa_real = df["Despesa realizada"].sum()

    # 🔹 RESULTADO REAL DO MÊS (SEM SALDO)
    resultado = receita_real - despesa_real

    # 🔹 SALDO FINAL
    saldo_final = saldo_inicial + resultado

    perc = (despesa_real / receita_real * 100) if receita_real > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("💰 Receita", f"R$ {receita_real:,.0f}")
    col2.metric("💸 Despesa", f"R$ {despesa_real:,.0f}")
    col3.metric("📊 Resultado (Mês)", f"R$ {resultado:,.0f}")
    col4.metric("🏦 Saldo Inicial", f"R$ {saldo_inicial:,.0f}")
    col5.metric("💼 Saldo Final", f"R$ {saldo_final:,.0f}")

    # Alertas baseados no RESULTADO (não no saldo)
    if resultado < 0:
        st.error("🚨 PREJUÍZO no mês")
    elif perc > 80:
        st.warning("⚠️ Alto comprometimento da receita")
    elif perc > 60:
        st.info("ℹ️ Atenção nas despesas")
    else:
        st.success("✅ Situação saudável")
