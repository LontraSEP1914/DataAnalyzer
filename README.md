# DataAnalyzer - Ferramenta de Confronto e Cruzamento de Dados

O **DataAnalyzer** é uma aplicação desktop desenvolvida para simplificar e automatizar o processo de comparação de dados entre dois arquivos (Excel ou CSV). A ferramenta permite que usuários realizem cruzamentos complexos, identifiquem divergências e gerem relatórios detalhados com facilidade e precisão.

Este projeto foi criado para automatizar o processo de confronto de dados, reduzindo a margem de erro em pelo menos 75% e garantindo entregas de maior qualidade, como mencionado no [meu portfólio](https://lontrasep1914.github.io/).

## ✨ Funcionalidades Principais

* **Interface Lado a Lado:** Carregue e configure dois arquivos (Lado A e Lado B) de forma independente em uma interface clara e organizada.
* **Chaves de Cruzamento Flexíveis:**
    * **Chave Simples ou Composta:** Selecione uma ou múltiplas colunas como chave para o cruzamento dos dados.
    * **Gerador de Chave Composta:** Crie uma nova coluna-chave na hora, concatenando os valores de outras colunas, para cruzamentos mais complexos.
* **Mapeamento de Colunas de Valor:** Defina múltiplos pares de colunas de valor para comparar entre os dois arquivos (ex: comparar a coluna "Valor Total" do Lado A com a "Vl_Recebido" do Lado B).
* **Filtros Pré-Cruzamento:** Aplique filtros em cada um dos lados antes de realizar o cruzamento, permitindo analisar subconjuntos específicos dos seus dados.
* **Controle do Tipo de Join:** Escolha o tipo de cruzamento que melhor se adapta à sua análise: `inner`, `left`, `right` ou `outer`.
* **Relatório Detalhado em Excel:** A ferramenta gera um relatório completo em Excel com duas abas:
    1.  **Resumo da Comparação:** Uma visão geral com os totais de cada lado e as diferenças absolutas e percentuais para cada par de colunas.
    2.  **Dados Detalhados:** O resultado do `merge` linha a linha, com colunas adicionais que calculam as diferenças absolutas e percentuais para cada registro.

## 🛠️ Tecnologias Utilizadas

* **Python:** Linguagem principal do projeto.
* **Pandas:** Para a manipulação e comparação dos DataFrames.
* **PyQt6:** Para a construção da interface gráfica desktop.
* **Openpyxl:** Para a geração e estilização dos relatórios em Excel.

## 🚀 Como Usar

1.  Clone o repositório.
2.  Instale as dependências: `pip install PyQt6 pandas openpyxl qdarktheme`.
3.  Execute `main.py` para iniciar a aplicação.
4.  Selecione os arquivos do "Lado A" e "Lado B".
5.  Escolha a(s) coluna(s)-chave para cada lado.
6.  Adicione um ou mais pares de colunas de valor para comparação.
7.  (Opcional) Configure filtros e ajuste o tipo de join.
8.  Clique em "Iniciar Confronto" e escolha onde salvar o relatório gerado.
