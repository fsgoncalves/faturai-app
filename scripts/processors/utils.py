import pandas as pd
import re

data_base = pd.Timestamp("2025-07-08")  # Tipo Timestamp (evita conflitos)

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
def processar_faturas(df,coluna_parcela='title'):
    novas_linhas = []

    for _, row in df.iterrows():
        row['parcela_atual'], row['parcela_final'] = extrair_parcelas(row[coluna_parcela])
        
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