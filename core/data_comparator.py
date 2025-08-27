# core/data_comparator.py

import pandas as pd
import numpy as np

# Helper function to apply a single filter to a DataFrame
def _aplicar_filtro_df(df: pd.DataFrame, filtro_info: dict) -> pd.DataFrame:
    """
    Aplica um filtro a um DataFrame com base nas informações fornecidas.

    Args:
        df (pd.DataFrame): O DataFrame a ser filtrado.
        filtro_info (dict): Um dicionário contendo {'coluna': str, 'operador': str, 'valor': str}.

    Returns:
        pd.DataFrame: O DataFrame filtrado. Pode retornar o DataFrame original se o filtro
                      for inválido ou não aplicável.
    """
    if not filtro_info or not filtro_info.get('coluna'):
        # print("Debug Filtro: filtro_info vazio ou sem coluna.")
        return df 

    coluna = filtro_info['coluna']
    operador = filtro_info['operador']
    valor_filtro_str = filtro_info['valor']

    if coluna not in df.columns:
        # print(f"Aviso de Filtro: Coluna de filtro '{coluna}' não encontrada no DataFrame. Filtro não aplicado.")
        return df

    serie_coluna = df[coluna]
    df_filtrado = df # Começa com o original, modifica se o filtro for bem-sucedido

    try:
        # Operadores que não usam o campo 'valor'
        if operador == 'é nulo':
            mask = serie_coluna.isna()
            df_filtrado = df[mask]
        elif operador == 'não é nulo':
            mask = serie_coluna.notna()
            df_filtrado = df[mask]
        
        # Operadores que usam o campo 'valor'
        # Para estes, se o valor_filtro_str for essencial e estiver vazio, não aplicar.
        elif not valor_filtro_str.strip() and operador not in ['é nulo', 'não é nulo']:
            # print(f"Aviso de Filtro: Valor para o operador '{operador}' na coluna '{coluna}' está vazio. Filtro não aplicado.")
            return df # Retorna original se valor é necessário mas não fornecido
        
        elif operador in ['>', '<', '>=', '<=']:
            # Tenta converter a coluna e o valor para numérico para comparação
            serie_numerica_coluna = pd.to_numeric(serie_coluna, errors='coerce')
            valor_numerico_filtro = float(valor_filtro_str) # Tenta converter, pode dar ValueError

            if operador == '>': mask = serie_numerica_coluna > valor_numerico_filtro
            elif operador == '<': mask = serie_numerica_coluna < valor_numerico_filtro
            elif operador == '>=': mask = serie_numerica_coluna >= valor_numerico_filtro
            elif operador == '<=': mask = serie_numerica_coluna <= valor_numerico_filtro
            df_filtrado = df[mask.fillna(False)] # NaNs na coluna não satisfazem o filtro numérico

        elif operador in ['=', '!=']:
            # Para igualdade/desigualdade, comparamos como string para robustez geral,
            # a menos que uma conversão numérica mútua seja bem-sucedida.
            # Isso evita problemas com "10" vs 10.0 vs "10.0"
            # Uma abordagem simples: converter a coluna para string e comparar com o valor do filtro (string).
            serie_str_coluna = serie_coluna.astype(str)
            # valor_filtro_str já é string
            if operador == '=': mask = serie_str_coluna.str.fullmatch(valor_filtro_str, case=False, na=False) # fullmatch para igualdade exata
            else: mask = ~serie_str_coluna.str.fullmatch(valor_filtro_str, case=False, na=False) # !=
            df_filtrado = df[mask]

        elif operador == 'contém':
            mask = serie_coluna.astype(str).str.contains(valor_filtro_str, case=False, na=False)
            df_filtrado = df[mask]
        elif operador == 'não contém':
            mask = ~serie_coluna.astype(str).str.contains(valor_filtro_str, case=False, na=False)
            df_filtrado = df[mask]
        elif operador == 'começa com':
            mask = serie_coluna.astype(str).str.startswith(valor_filtro_str, na=False)
            df_filtrado = df[mask]
        elif operador == 'termina com':
            mask = serie_coluna.astype(str).str.endswith(valor_filtro_str, na=False)
            df_filtrado = df[mask]
        else:
            # print(f"Aviso de Filtro: Operador '{operador}' desconhecido. Filtro não aplicado.")
            return df # Retorna original

        # print(f"Filtro aplicado: Coluna='{coluna}', Operador='{operador}', Valor='{valor_filtro_str}'. Linhas restantes: {len(df_filtrado)}")
        return df_filtrado

    except ValueError: # Captura erro de conversão de valor_filtro_str para float/int
        # print(f"Aviso de Filtro: Valor '{valor_filtro_str}' inválido para operador numérico '{operador}' na coluna '{coluna}'. Filtro não aplicado.")
        return df # Retorna original se o valor for inválido para o operador
    except Exception as e:
        # print(f"Erro inesperado ao aplicar filtro na coluna '{coluna}' com operador '{operador}': {e}")
        import traceback; traceback.print_exc()
        return df # Retorna original em caso de outro erro


def comparar_dataframes(df_lado_a: pd.DataFrame,
                        df_lado_b: pd.DataFrame,
                        colunas_chave_a: list[str],
                        colunas_chave_b: list[str], 
                        pares_mapeados: list[tuple[str, str]],
                        tipo_join: str = 'inner'
                        # Parâmetros de filtro removidos daqui, pois já são aplicados na GUI
                        ) -> dict | None:
    """
    Compara pares de colunas de valor, usando uma ou mais colunas chave para o join.
    """
    try:
        df_a_processado = df_lado_a.copy()
        df_b_processado = df_lado_b.copy()

        # A lógica de filtro agora é feita na GUI antes de chamar esta função

        cols_a_originais_dos_pares = list(set([par[0] for par in pares_mapeados]))
        cols_b_originais_dos_pares = list(set([par[1] for par in pares_mapeados]))

        renamed_cols_a_map = {}
        for col_orig_a in cols_a_originais_dos_pares:
            # checar se a coluna está na LISTA de chaves
            if col_orig_a in colunas_chave_a: 
                renamed_cols_a_map[col_orig_a] = col_orig_a
                continue
            if col_orig_a in df_a_processado.columns:
                suffixed_name = f"{col_orig_a}_A"
                df_a_processado.rename(columns={col_orig_a: suffixed_name}, inplace=True)
                renamed_cols_a_map[col_orig_a] = suffixed_name
            
        renamed_cols_b_map = {}
        for col_orig_b in cols_b_originais_dos_pares:
            # checar se a coluna está na LISTA de chaves
            if col_orig_b in colunas_chave_b: 
                renamed_cols_b_map[col_orig_b] = col_orig_b
                continue
            if col_orig_b in df_b_processado.columns:
                suffixed_name = f"{col_orig_b}_B"
                df_b_processado.rename(columns={col_orig_b: suffixed_name}, inplace=True)
                renamed_cols_b_map[col_orig_b] = suffixed_name

        # --- MUDANÇA PRINCIPAL NA CHAMADA DO MERGE ---
        df_merged = pd.merge(
            df_a_processado,
            df_b_processado,
            left_on=colunas_chave_a,  # Passando a lista
            right_on=colunas_chave_b, # Passando a lista
            how=tipo_join,
            suffixes=('_dfA', '_dfB')
        )
        # -----------------------------------------------

        if df_merged.empty:
             print(f"Aviso DataComparator: O merge (tipo '{tipo_join}') resultou em um DataFrame vazio.")
             return {'resumo_por_par': [], 'dataframe_merged': df_merged}

        lista_resultados_resumo_pares = []
        for nome_col_a_original, nome_col_b_original in pares_mapeados:
            col_a_no_merge = renamed_cols_a_map.get(nome_col_a_original)
            col_b_no_merge = renamed_cols_b_map.get(nome_col_b_original)
            if not col_a_no_merge or col_a_no_merge not in df_merged.columns: continue
            if not col_b_no_merge or col_b_no_merge not in df_merged.columns: continue
            val_a_numeric_par = pd.to_numeric(df_merged[col_a_no_merge], errors='coerce')
            val_b_numeric_par = pd.to_numeric(df_merged[col_b_no_merge], errors='coerce')
            soma_col_a = val_a_numeric_par.fillna(0); soma_col_b = val_b_numeric_par.fillna(0)
            total_lado_a_par = soma_col_a.sum(); total_lado_b_par = soma_col_b.sum()
            diferenca_absoluta_total_par = total_lado_a_par - total_lado_b_par
            if total_lado_b_par != 0: diferenca_percentual_total_par = (diferenca_absoluta_total_par / total_lado_b_par) * 100
            elif total_lado_a_par != 0: diferenca_percentual_total_par = 100.0 if diferenca_absoluta_total_par != 0 else 0.0
            else: diferenca_percentual_total_par = 0.0
            nome_descritivo_par = f"{nome_col_a_original} (A) vs {nome_col_b_original} (B)"
            lista_resultados_resumo_pares.append({
                'par_comparado': nome_descritivo_par, 'total_lado_a': total_lado_a_par,
                'total_lado_b': total_lado_b_par, 'diferenca_absoluta_total': diferenca_absoluta_total_par,
                'diferenca_percentual_total': diferenca_percentual_total_par
            })
            base_nome_diff = f"{nome_col_a_original}_vs_{nome_col_b_original}"
            nome_diff_abs_linha = f'{base_nome_diff}_DiffAbs_Linha'
            nome_diff_perc_linha = f'{base_nome_diff}_DiffPerc_Linha(%)'
            df_merged[nome_diff_abs_linha] = soma_col_a - soma_col_b
            denominador_perc = val_b_numeric_par.copy(); denominador_perc.replace(0, np.nan, inplace=True)
            df_merged[nome_diff_perc_linha] = np.where(
                denominador_perc.notna(), (df_merged[nome_diff_abs_linha] / denominador_perc) * 100,
                np.where(soma_col_a != 0, np.inf * np.sign(soma_col_a), 0)
            )
            df_merged[nome_diff_perc_linha] = df_merged[nome_diff_perc_linha].apply(
                lambda x: round(x, 2) if pd.notna(x) and x not in [np.inf, -np.inf] else x
            )

        return {
            'resumo_por_par': lista_resultados_resumo_pares,
            'dataframe_merged': df_merged
        }

    except KeyError as ke:
        # print(f"Erro de Chave (KeyError) durante a comparação: {ke}.")
        return None
    except Exception as e:
        # print(f"Ocorreu um erro inesperado durante a comparação: {e}")
        import traceback; traceback.print_exc()
        return None

if __name__ == '__main__':
    from excel_parser import carregar_dados_excel 
    import os

    print("--- Testando Comparador com Filtros (Backend) ---")
    
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(current_file_dir) 
    exemplos_dir = os.path.join(base_dir, 'exemplos_excel')
    if not os.path.exists(exemplos_dir): os.makedirs(exemplos_dir)

    caminho_ex_a = os.path.join(exemplos_dir, 'filter_test_A.xlsx')
    caminho_ex_b = os.path.join(exemplos_dir, 'filter_test_B.xlsx')

    # Dados mais completos para teste de filtro
    dados_a = {
        'ID': [1, 2, 3, 4, 5, 6], 
        'Produto': ['Caneta Azul', 'Lapis Grafite', 'Borracha Branca', 'Regua 30cm', 'Caneta Vermelha', 'Caderno 10 Mat'],
        'Valor': [2.50, 1.00, 0.75, 3.00, 2.50, 15.00], 
        'Regiao': ['Sul', 'Sudeste', 'Sul', 'Norte', 'Sudeste', 'Nordeste'],
        'Data': pd.to_datetime(['2024-01-10', '2024-01-15', '2024-02-01', '2024-02-05', '2024-03-10', '2024-03-12'])
    }
    pd.DataFrame(dados_a).to_excel(caminho_ex_a, index=False)

    dados_b = {
        'ItemID': [1, 2, 3, 4, 5, 7], # ID 6 falta em B, ID 7 novo em B
        'Descricao': ['CAN AZL', 'LPS GRF', 'BOR BRNC', 'REGUA 30', 'CAN VERM', 'APONTADOR'],
        'Preco': [2.50, 1.20, 0.70, 3.00, 2.60, 4.00], 
        'Estoque': [100, 150, 200, 80, 120, 50],
        'Status': ['Ativo', 'Ativo', 'Inativo', 'Ativo', 'Ativo', 'Ativo']
    }
    pd.DataFrame(dados_b).to_excel(caminho_ex_b, index=False)
    print(f"Arquivos de exemplo para filtro '{caminho_ex_a}' e '{caminho_ex_b}' criados/atualizados.")

    df_a_teste_filt = carregar_dados_excel(caminho_ex_a)
    df_b_teste_filt = carregar_dados_excel(caminho_ex_b)

    if df_a_teste_filt is not None and df_b_teste_filt is not None:
        pares_mapeados_teste = [('Valor', 'Preco')] # Comparar 'Valor' de A com 'Preco' de B
        
        print("\n--- Teste Filtro: Lado A: Regiao = 'Sul' ---")
        filtro_a_ex = {'coluna': 'Regiao', 'operador': '=', 'valor': 'Sul'}
        resultados_f1 = comparar_dataframes(
            df_lado_a=df_a_teste_filt.copy(), df_lado_b=df_b_teste_filt.copy(),
            coluna_chave_a='ID', coluna_chave_b='ItemID',
            pares_mapeados=pares_mapeados_teste, tipo_join='inner',
            filtro_info_a=filtro_a_ex
        )
        if resultados_f1: 
            print(f"Resumo (Filtro A Regiao=Sul): {resultados_f1['resumo_por_par']}")
            print(f"DF Merged (Filtro A Regiao=Sul) tem {len(resultados_f1['dataframe_merged'])} linhas.")
            print(resultados_f1['dataframe_merged'].head())

        print("\n--- Teste Filtro: Lado B: Estoque >= 100 ---")
        filtro_b_ex = {'coluna': 'Estoque', 'operador': '>=', 'valor': '100'}
        resultados_f2 = comparar_dataframes(
            df_lado_a=df_a_teste_filt.copy(), df_lado_b=df_b_teste_filt.copy(),
            coluna_chave_a='ID', coluna_chave_b='ItemID',
            pares_mapeados=pares_mapeados_teste, tipo_join='inner',
            filtro_info_b=filtro_b_ex
        )
        if resultados_f2: 
            print(f"Resumo (Filtro B Estoque>=100): {resultados_f2['resumo_por_par']}")
            print(f"DF Merged (Filtro B Estoque>=100) tem {len(resultados_f2['dataframe_merged'])} linhas.")
            print(resultados_f2['dataframe_merged'].head())

        print("\n--- Teste Filtro: Lado A: Produto contém 'Caneta' E Lado B: Status = 'Ativo' ---")
        filtro_a_ex3 = {'coluna': 'Produto', 'operador': 'contém', 'valor': 'Caneta'}
        filtro_b_ex3 = {'coluna': 'Status', 'operador': '=', 'valor': 'Ativo'}
        resultados_f3 = comparar_dataframes(
            df_lado_a=df_a_teste_filt.copy(), df_lado_b=df_b_teste_filt.copy(),
            coluna_chave_a='ID', coluna_chave_b='ItemID',
            pares_mapeados=pares_mapeados_teste, tipo_join='outer', # Outer para ver efeito dos filtros
            filtro_info_a=filtro_a_ex3,
            filtro_info_b=filtro_b_ex3
        )
        if resultados_f3:
            print(f"Resumo (Filtro Ambos): {resultados_f3['resumo_por_par']}")
            print(f"DF Merged (Filtro Ambos) tem {len(resultados_f3['dataframe_merged'])} linhas.")
            print(resultados_f3['dataframe_merged']) # Mostrar mais linhas
            # print(list(resultados_f3['dataframe_merged'].columns)) # Para ver todas as colunas

        print("\n--- Teste Filtro: Lado A: Data > 2024-02-01 (teste de data como string) ---")
        # Nota: Filtragem de data robusta precisaria de conversão para datetime
        # Esta é uma comparação de string, pode não funcionar como esperado para datas.
        filtro_a_ex_data = {'coluna': 'Data', 'operador': '>', 'valor': '2024-02-01'}
        # Para que o teste de '>' com data funcione melhor, converteremos a coluna de Data para string no formato YYYY-MM-DD
        df_a_data_str = df_a_teste_filt.copy()
        df_a_data_str['Data'] = pd.to_datetime(df_a_data_str['Data']).dt.strftime('%Y-%m-%d')

        resultados_f_data = comparar_dataframes(
            df_lado_a=df_a_data_str, df_lado_b=df_b_teste_filt.copy(),
            coluna_chave_a='ID', coluna_chave_b='ItemID',
            pares_mapeados=pares_mapeados_teste, tipo_join='inner',
            filtro_info_a=filtro_a_ex_data
        )
        if resultados_f_data:
            print(f"Resumo (Filtro Data A > '2024-02-01'): {resultados_f_data['resumo_por_par']}")
            print(f"DF Merged (Filtro Data A) tem {len(resultados_f_data['dataframe_merged'])} linhas.")
            print(resultados_f_data['dataframe_merged'].head())


    else:
        print("Erro ao carregar DataFrames para teste de filtros.")