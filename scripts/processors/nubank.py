import pandas as pd
from processors.utils import processar_faturas

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

# ========================
# Upload e processamento
# ========================

def processar_arquivo_nubank(uploaded_file):
    # Leitura do arquivo conforme o tipo
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    else:
        df = pd.read_excel(uploaded_file)

    df['date'] = pd.to_datetime(df['date'])
    df = df[df['amount'] > 0]
    df['categoria'] = df['title'].apply(classificar_categoria)

    df_resultado = processar_faturas(df)

    df_resultado = df_resultado.rename(columns={
        'title': 'lancamento',
        'amount': 'valor'
    })

    return df_resultado