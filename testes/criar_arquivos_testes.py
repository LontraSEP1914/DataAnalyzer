import pandas as pd
import os

# --- DESCRIÇÃO DOS DADOS DE TESTE ---

# Cenário 1: Vendas vs. Estoque (para Confronto e Cruzamentos)
dados_vendas = {
    'ID_Produto': [101, 102, 103, 104, 105, 108],
    'Nome_Produto': ['Teclado Mecânico', 'Mouse Gamer RGB', 'Monitor 24"', 'Headset 7.1', 'Webcam 4K', 'Cadeira Gamer'],
    'Valor_Venda': [350.50, 180.00, 950.99, 450.00, 620.00, 1250.80],
    'Data': pd.to_datetime(['2024-03-10', '2024-03-10', '2024-03-11', '2024-03-12', '2024-03-12', '2024-03-15'])
}

dados_estoque = {
    'SKU': [101, 102, 103, 104, 106, 107],
    'Produto_Estoque': ['Teclado Mec.', 'Mouse RGB', 'Monitor 24 Pol', 'Headset Gamer', 'SSD 1TB', 'Gabinete ATX'],
    'Preco_Custo': [280.00, 150.50, 899.00, 460.50, 480.00, 350.00],
    'Quantidade': [50, 75, 30, 40, 60, 25]
}
# Casos de teste aqui:
# - IDs 101, 102, 103, 104: Existem em ambos (ideal para inner join e confronto).
# - ID 105, 108: Apenas em Vendas (ideal para left/outer join).
# - ID 106, 107: Apenas em Estoque (ideal para right/outer join).
# - Valor_Venda vs Preco_Custo: Ideal para o modo Confronto.

# Cenário 2: Pedidos Online vs. Faturamento (para teste de filtros)
dados_pedidos = {
    'ID_Pedido': [1, 2, 3, 4, 5, 6, 7],
    'Cliente': ['Ana Silva', 'Bruno Costa', 'Carlos Dias', 'Daniela Souza', 'Eduardo Lima', 'Fernanda Mota', 'Gustavo Borges'],
    'Regiao': ['Sudeste', 'Sul', 'Nordeste', 'Sudeste', 'Sul', 'Centro-Oeste', 'Nordeste'],
    'Valor_Total': [150.00, 88.50, 230.00, 45.90, 120.00, 510.80, 75.25],
    'Status': ['Entregue', 'Enviado', 'Entregue', 'Cancelado', 'Enviado', 'Processando', 'Entregue']
}

dados_faturamento = {
    'Fatura_ID': [1, 2, 3, 4, 5, 8],
    'Nome_Cliente_Fat': ['Ana Silva', 'Bruno Costa', 'Carlos Dias', 'Daniela S.', 'Eduardo Lima', 'Helena Reis'],
    'Valor_Faturado': [150.00, 90.00, 230.00, 45.90, 125.50, 200.00],
    'Status_Pgto': ['Pago', 'Pago', 'Pendente', 'Estornado', 'Pago', 'Pago']
}
# Casos de teste aqui:
# - Filtro por Regiao='Sudeste' ou Status='Enviado' em Pedidos.
# - Filtro por Status_Pgto='Pago' em Faturamento.
# - Confronto entre Valor_Total e Valor_Faturado (com pequenas discrepâncias nos IDs 2 e 5).
# - Cruzamento por outer join para encontrar pedidos sem fatura (6, 7) e faturas sem pedido (8).

def criar_arquivos():
    """Cria a pasta e os arquivos Excel de exemplo."""
    pasta_destino = 'exemplos_teste'
    if not os.path.exists(pasta_destino):
        os.makedirs(pasta_destino)
        print(f'Pasta "{pasta_destino}" criada.')

    # Criar DataFrames
    df_vendas = pd.DataFrame(dados_vendas)
    df_estoque = pd.DataFrame(dados_estoque)
    df_pedidos = pd.DataFrame(dados_pedidos)
    df_faturamento = pd.DataFrame(dados_faturamento)

    # Caminhos dos arquivos
    caminho_vendas = os.path.join(pasta_destino, 'Vendas_Sistema_A.xlsx')
    caminho_estoque = os.path.join(pasta_destino, 'Estoque_Sistema_B.xlsx')
    caminho_pedidos = os.path.join(pasta_destino, 'Pedidos_Online.xlsx')
    caminho_faturamento = os.path.join(pasta_destino, 'Faturamento_ERP.xlsx')

    # Salvar em Excel
    df_vendas.to_excel(caminho_vendas, index=False)
    df_estoque.to_excel(caminho_estoque, index=False)
    df_pedidos.to_excel(caminho_pedidos, index=False)
    df_faturamento.to_excel(caminho_faturamento, index=False)

    print(f'Arquivos de teste criados com sucesso na pasta "{pasta_destino}":')
    print(f'- {os.path.basename(caminho_vendas)}')
    print(f'- {os.path.basename(caminho_estoque)}')
    print(f'- {os.path.basename(caminho_pedidos)}')
    print(f'- {os.path.basename(caminho_faturamento)}')

if __name__ == '__main__':
    criar_arquivos()