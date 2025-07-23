import streamlit as st
import pandas as pd
import re

# Configuração inicial
st.set_page_config(page_title="FaturAI", layout="wide")
st.title("📊 FaturAI - Análise Inteligente de Faturas")

# Definição da data base para vencimento da fatura
data_base = pd.Timestamp("2025-07-08")  # Tipo Timestamp (evita conflitos)

# ========================
# Funções auxiliares
# ========================

# Classifica a categoria com base no título
def classificar_categoria(title):
    title = str(title).lower()

    if any(x in title for x in ["farmacia", "dimed", "panvel", "raia"]):
        return "Farmácia"
    elif any(x in title for x in ["bourbon", "carrefour", "lahude", "cestto", "zaffari", "pkr comercio"]):
        return "Mercado"
    elif any(x in title for x in ["clinica de vacinas", "colchoes ortobom"]):
        return "Saúde"
    elif any(x in title for x in ["belshop", "oboticario", "perfumes e prese"]):
        return "Beleza"
    elif any(x in title for x in ["aquila", "produtos globo", "amazon", "multiplos esportes", "villaggio", "pampa burguer"]):
        return "Lazer"
    elif any(x in title for x in ["kiwify", "google one", "nio fibra"]):
        return "Educação"
    elif any(x in title for x in ["lojas renner", "shein"]):
        return "Vestuário"
    elif any(x in title for x in ["lyon park", "sigapay"]):
        return "Estacionamento"
    elif any(x in title for x in ["surdinas car"]):
        return "Manutenção Veicular"
    elif any(x in title for x in ["centervatti"]):
        return "Manutenção Predial"
    elif any(x in title for x in ["uber"]):
        return "Mobilidade"
    elif any(x in title for x in ["mercadolivre", "motorola", "conta vivo"]):
        return "Compras Online"
    else:
        return "Outros"



# Extrai número da parcela atual e total (ex: 2/10)
def extrair_parcelas(title):
    resultado = re.search(r'(\d+)\s*/\s*(\d+)', str(title))
    if resultado:
        return int(resultado.group(1)), int(resultado.group(2))
    else:
        return 1, 1  # Considera como parcela única se não houver padrão

# Gera novas linhas com as parcelas futuras
def gerar_parcelas(row):
    linhas = []
    diferenca = row['parcela_final'] - row['parcela_atual']
    for i in range(diferenca + 1):
        nova_linha = row.copy()
        nova_linha['data_vcto'] = data_base + pd.DateOffset(months=i)
        nova_linha['parcela'] = f"{row['parcela_atual'] + i}/{row['parcela_final']}"
        linhas.append(nova_linha)
    return linhas

# Processa o DataFrame: extrai, explode e retorna novo DataFrame
def processar_faturas(df):
    novas_linhas = []

    for _, row in df.iterrows():
        row['parcela_atual'], row['parcela_final'] = extrair_parcelas(row['title'])
        
        if row['parcela_final'] > 1:
            novas_linhas.extend(gerar_parcelas(row))
        else:
            row['data_vcto'] = data_base  # Corrigido para fixar no mês 7
            row['parcela'] = None
            novas_linhas.append(row)

    df_resultado = pd.DataFrame(novas_linhas)

    # Garante que data_vcto seja Timestamp
    df_resultado['data_vcto'] = pd.to_datetime(df_resultado['data_vcto'])

    return df_resultado.drop(columns=['parcela_atual', 'parcela_final'], errors='ignore')

# ========================
# Upload e processamento
# ========================

uploaded_file = st.file_uploader("📎 Carregue sua fatura (CSV ou Excel)", type=["csv", "xls", "xlsx"])

if uploaded_file:
    try:
        # Leitura do arquivo conforme o tipo
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')
        else:
            df = pd.read_excel(uploaded_file)

        # Converte coluna de data
        df['date'] = pd.to_datetime(df['date'])

        # Somente valores maiores do que zero
        df = df[df['amount'] > 0]

        df['categoria'] = df['title'].apply(classificar_categoria)

        # Processa faturas (explosão de parcelas)
        df_resultado = processar_faturas(df)

        # Exibição
        st.success("✅ Arquivo processado com sucesso!")
        st.subheader("📅 Faturas com parcelas expandidas:")
        st.dataframe(
            df_resultado[['data_vcto', 'title', 'categoria','amount', 'parcela']].sort_values(by='data_vcto').reset_index(drop=True)
        )

        # Campo de renda
        renda_mensal = st.number_input("💰 Informe sua renda mensal (R$)", min_value=0.0, format="%.2f")

        # Cálculo do comprometimento da renda
        if renda_mensal > 0:
            df_resultado['mes'] = df_resultado['data_vcto'].dt.to_period("M").astype(str)

            resumo = df_resultado.groupby('mes').agg(
                total_gastos=('amount', 'sum')
            ).reset_index()

            resumo['percentual_renda'] = (resumo['total_gastos'] / renda_mensal * 100).round(1)

            st.subheader("📊 Comprometimento da Renda por Mês")
            st.dataframe(resumo)

            st.line_chart(resumo.set_index('mes')[['percentual_renda']])

        # Distribuição de gastos por categoria
            st.subheader("📊 Gastos por Categoria ao Longo dos Meses")

            df_resultado['mes'] = df_resultado['data_vcto'].dt.to_period("M").astype(str)

            # Total por mês e categoria
            df_cat_mes = df_resultado.groupby(['mes', 'categoria']).agg(
                total_gasto=('amount', 'sum')
            ).reset_index()

            # Tabela pivô para visualização
            df_pivot = df_cat_mes.pivot(index='mes', columns='categoria', values='total_gasto').fillna(0)

            st.dataframe(df_pivot)

            # Gráfico de barras agrupadas por mês
            st.bar_chart(df_pivot)


    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
