# core/excel_parser.py

import pandas as pd
import os

def carregar_dados_excel(caminho_arquivo: str, colunas_para_ler: list = None) -> pd.DataFrame | None:
    """
    Carrega dados de um arquivo Excel ou CSV, selecionando colunas específicas.

    Args:
        caminho_arquivo (str): O caminho para o arquivo.
        colunas_para_ler (list, optional): Colunas a serem lidas. Defaults to None (ler todas).

    Returns:
        pd.DataFrame | None: Um DataFrame do Pandas ou None em caso de erro.
    """
    # Obter a extensão do arquivo em minúsculas
    _, extensao = os.path.splitext(caminho_arquivo.lower())

    try:
        if extensao in ['.xlsx', '.xls']:
            # Para Excel, não precisamos passar sheet_name se quisermos a primeira
            df = pd.read_excel(caminho_arquivo, usecols=colunas_para_ler)
        elif extensao == '.csv':
            # pd.read_csv é muito rápido. Tenta detectar separador e lida com erros de encoding.
            df = pd.read_csv(caminho_arquivo, usecols=colunas_para_ler, 
                             sep=None, # Tenta detectar o separador automaticamente
                             engine='python', # 'python' é mais lento mas melhor na detecção de sep
                             encoding_errors='replace') # Lida com erros de encoding
        else:
            print(f"Erro: Formato de arquivo não suportado: '{extensao}'")
            return None

        print(f"Arquivo '{os.path.basename(caminho_arquivo)}' lido com sucesso.")
        return df

    except FileNotFoundError:
        print(f"Erro: O arquivo '{caminho_arquivo}' não foi encontrado.")
        return None
    except ValueError as ve: # Pode ser lançado por 'usecols' se a coluna não existir
        print(f"Erro de Valor ao ler o arquivo '{caminho_arquivo}': {ve}")
        return None
    except Exception as e:
        print(f"Ocorreu um erro inesperado ao ler o arquivo '{caminho_arquivo}': {e}")
        return None

if __name__ == '__main__':
    # Exemplo de como usar a função (para testes rápidos)
    # Crie um arquivo 'exemplo.xlsx' na pasta 'exemplos_excel' para testar
    # com algumas colunas como 'ID', 'Nome', 'Valor', 'Data'

    # Criar um DataFrame de exemplo e salvar como Excel para teste
    dados_exemplo = {
        'ID': [1, 2, 3, 4],
        'Nome': ['Produto A', 'Produto B', 'Produto C', 'Produto D'],
        'Valor': [100, 150, 200, 250],
        'Data': pd.to_datetime(['2024-01-01', '2024-01-15', '2024-02-01', '2024-02-10'])
    }
    df_exemplo = pd.DataFrame(dados_exemplo)
    
    # Crie a pasta se não existir (apenas para este exemplo de teste)
    import os
    if not os.path.exists('../exemplos_excel'):
        os.makedirs('../exemplos_excel')
    caminho_exemplo = '../exemplos_excel/exemplo_teste.xlsx'
    df_exemplo.to_excel(caminho_exemplo, index=False, sheet_name='Vendas')
    
    print(f"Arquivo de exemplo '{caminho_exemplo}' criado com a planilha 'Vendas'.")

    # Teste 1: Carregar colunas específicas da planilha 'Vendas'
    print("\n--- Teste 1 ---")
    df_lido1 = carregar_dados_excel(caminho_exemplo, nome_planilha='Vendas', colunas_para_ler=['ID', 'Valor'])
    if df_lido1 is not None:
        print("DataFrame Lido (Teste 1):")
        print(df_lido1.head())

    # Teste 2: Tentar carregar uma planilha que não existe
    print("\n--- Teste 2 ---")
    df_lido2 = carregar_dados_excel(caminho_exemplo, nome_planilha='Compras', colunas_para_ler=['ID', 'Valor'])
    if df_lido2 is not None:
        print(df_lido2.head()) # Não deve imprimir se o tratamento de erro funcionar

    # Teste 3: Tentar carregar um arquivo que não existe
    print("\n--- Teste 3 ---")
    df_lido3 = carregar_dados_excel('arquivo_inexistente.xlsx', colunas_para_ler=['ID', 'Valor'])
    if df_lido3 is not None:
        print(df_lido3.head()) # Não deve imprimir

    # Teste 4: Carregar todas as colunas da primeira planilha (sem especificar nome_planilha ou colunas_para_ler)
    # Nota: Para o 'usecols=None' funcionar bem como "ler todas as colunas",
    # é o comportamento padrão do pandas.read_excel se usecols não for passado.
    print("\n--- Teste 4 ---")
    df_lido4 = carregar_dados_excel(caminho_exemplo, nome_planilha='Vendas') # usecols=None é implícito
    if df_lido4 is not None:
        print("DataFrame Lido (Teste 4 - todas as colunas da planilha 'Vendas'):")
        print(df_lido4.head())

    # Teste 5: Tentar carregar colunas que não existem
    print("\n--- Teste 5 ---")
    df_lido5 = carregar_dados_excel(caminho_exemplo, nome_planilha='Vendas', colunas_para_ler=['ID', 'NaoExiste'])
    if df_lido5 is not None:
        print("DataFrame Lido (Teste 5):")
        print(df_lido5.head()) # pandas deve gerar um ValueError que é capturado