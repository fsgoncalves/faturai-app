import streamlit as st
import pandas as pd
from processors.nubank import processar_arquivo_nubank
from processors.banco_inter import processar_arquivo_inter

# Configuração da página
st.set_page_config(page_title="FaturAI", layout="wide")
st.title("📊 FaturAI - Análise Inteligente de Faturas")

# Inicializa session_state para armazenar os arquivos processados
if "faturas_processadas" not in st.session_state:
    st.session_state["faturas_processadas"] = {}

# Upload de múltiplos arquivos
uploaded_files = st.file_uploader("📎 Carregue uma ou mais faturas (CSV ou Excel)", type=["csv", "xls", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for uploaded_file in uploaded_files:
        nome_arquivo = uploaded_file.name

        with st.expander(f"📄 {nome_arquivo}", expanded=True):
            layout = st.selectbox("Layout da fatura", ["Nubank", "Banco Inter"], key=f"layout_{nome_arquivo}")

            vencimento = st.date_input(
                "📅 Data de vencimento da fatura",
                key=f"vencimento_{nome_arquivo}"
            )

            if st.button(f"Processar {nome_arquivo}", key=f"processar_{nome_arquivo}"):
                try:
                    # Processamento de acordo com o layout
                    if layout == "Nubank":
                        df_resultado = processar_arquivo_nubank(uploaded_file, vencimento)
                    elif layout == "Banco Inter":
                        df_resultado = processar_arquivo_inter(uploaded_file, vencimento)
                    else:
                        st.warning("⚠️ Layout não suportado.")
                        continue

                    # Padroniza colunas
                    df_resultado = df_resultado.rename(columns={
                        "data_vcto": "data_vcto",
                        "title": "lancamento",
                        "amount": "valor",
                        "categoria": "categoria",
                        "parcela": "parcela"
                    })

                    df_resultado["mes"] = df_resultado["data_vcto"].dt.to_period("M").astype(str)

                    # Salva no session_state
                    st.session_state["faturas_processadas"][nome_arquivo] = df_resultado
                    st.success("✅ Arquivo processado com sucesso!")

                except Exception as e:
                    st.error(f"❌ Erro ao processar o arquivo {nome_arquivo}: {e}")

# Mostra resultados apenas se houver dados processados
if st.session_state["faturas_processadas"]:
    df_consolidado = pd.concat(
        st.session_state["faturas_processadas"].values(),
        ignore_index=True
    )

    st.divider()
    st.subheader("📅 Faturas Consolidadas com Parcelas Expandidas")
    st.dataframe(
        df_consolidado[["data_vcto", "lancamento", "categoria", "valor", "parcela"]]
        .sort_values(by="data_vcto")
        .reset_index(drop=True)
    )

    # Campo de renda
    renda_mensal = st.number_input("💰 Informe sua renda mensal (R$)", min_value=0.0, format="%.2f")

    if renda_mensal > 0:
        resumo = df_consolidado.groupby("mes").agg(
            total_gastos=("valor", "sum")
        ).reset_index()

        resumo["percentual_renda"] = (resumo["total_gastos"] / renda_mensal * 100).round(1)

        st.subheader("📊 Comprometimento da Renda por Mês")
        st.dataframe(resumo)
        st.line_chart(resumo.set_index("mes")[["percentual_renda"]])

        st.subheader("📊 Gastos por Categoria ao Longo dos Meses")

        df_cat_mes = df_consolidado.groupby(["mes", "categoria"]).agg(
            total_gasto=("valor", "sum")
        ).reset_index()

        df_pivot = df_cat_mes.pivot(index="mes", columns="categoria", values="total_gasto").fillna(0)

        st.dataframe(df_pivot)
        st.bar_chart(df_pivot)
