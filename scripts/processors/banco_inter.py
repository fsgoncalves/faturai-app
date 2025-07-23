import pandas as pd
from processors.utils import processar_faturas

def classificar_categoria(tipo):
    tipo = str(tipo).lower()

    if any(x in tipo for x in ["drogaria"]):
        return "Farmácia"
    elif any(x in tipo for x in ["supermercado"]):
        return "Mercado"
    elif any(x in tipo for x in ["transporte"]):
        return "Mobilidade"
    elif any(x in tipo for x in ["construcao"]):
        return "Manutenção Predial"
    elif any(x in tipo for x in ["compras"]):
        return "Lazer"
    elif any(x in tipo for x in ["ensino"]):
        return "Educação"
    elif any(x in tipo for x in ["outros","pagamentos"]):
        return "Outros"
    elif any(x in tipo for x in ["vestuario"]):
        return "Vestuário"
    else:
        return "Outros"

# ========================
# Upload e processamento
# ========================

def processar_arquivo_inter(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, sep=None, engine='python')
    else:
        df = pd.read_excel(uploaded_file)

    # Limpeza de colunas (defensivo contra BOM, aspas e espaços)
    df.columns = df.columns.str.replace('"', '', regex=False)
    df.columns = df.columns.str.replace('\ufeff', '', regex=False)
    df.columns = df.columns.str.strip()

    # Agora sim o rename
    df = df.rename(columns={
        'Data': 'date',
        'Lançamento': 'title',
        'Categoria': 'categoria',
        'Tipo': 'tipo',
        'Valor': 'amount'
    })

    # Remove espaços extras ou caracteres invisíveis nos nomes das colunas
    df.columns = df.columns.str.strip()

    # Renomeia as colunas
    df = df.rename(columns={
        'Data': 'date',
        'Lançamento': 'title',
        'Categoria': 'categoria',
        'Tipo': 'tipo',
        'Valor': 'amount'
    })

    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
    df = df[df['title'] != 'PAGTO DEBITO AUTOMATICO']

    df['amount'] = (
        df['amount']
        .astype(str)
        .str.replace(r'R\$', '', regex=True)
        .str.replace(u'\xa0', '', regex=True)
        .str.replace(' ', '')
        .str.replace(',', '.')
        .astype(float)
    )

    df = df[df['amount'] > 0]
    df['categoria'] = df['categoria'].apply(classificar_categoria)

    df_resultado = processar_faturas(df, coluna_parcela='tipo')

    return df_resultado[['data_vcto', 'title', 'categoria', 'amount', 'parcela']]
