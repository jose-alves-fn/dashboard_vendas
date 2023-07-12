import streamlit as st
import requests
import pandas as pd
import time
from io import BytesIO
import xlsxwriter


# Funcoes para dowload de arquivos
## Dowmload de .csv
@st.cache_data # Decorator necessário para evitar a geração contínua de muitos arquivos iguais
def converte_csv(df):
    return df.to_csv(index = False).encode('utf-8')

## Dowmload de .xlsx
@st.cache_data # Decorator necessário para evitar a geração contínua de muitos arquivos iguais
def converte_xlsx(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter', datetime_format='yyyy-mm-dd', date_format='yyyy-mm-dd') as writer:  # Para valores de datas constantes no df
        df.to_excel(writer, index=False)   # Chamada da funcao do pandas to_excel
        workbook = writer.book  # workbook é uma variável que representa o objeto do livro do Excel (Workbook) associado ao ExcelWriter (objeto writer).         
        worksheet = writer.sheets['Sheet1'] # worksheet é uma variável que representa uma planilha específica dentro do livro do Excel. 
        header_format = workbook.add_format({'border': False}) # header_format é uma variável que representa um objeto de formatação (Format) no workbook
        for col_num, value in enumerate(df.columns.values): # Usando workbook.add_format(), criamos um novo objeto de formatação e o associamos ao workbook (livro do Excel)
            worksheet.write(0, col_num, value, header_format)
    output.seek(0) # mover o cursor de leitura/escrita para a posição 0 (início) no fluxo de bytes.
    return output.getvalue()


## Mensagem de sucesso
def mensagem_sucesso():
    sucesso = st.success('Arquivo baixado com sucesso!', icon="✅")
    time.sleep(7)  
    sucesso.empty()


st.title('TABELA DE DADOS')

url = 'https://labdados.com/produtos'

response = requests.get(url)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')

# Adicionando filtros à página de dados
with st.expander('Colunas'):
    colunas = st.multiselect('Selecione as colunas', list(dados.columns), list(dados.columns))

# Adicionando filtros à barra lateral
st.sidebar.title('Filtros')
with st.sidebar.expander('Nome do produto'):  # 03 parametros no multiselect, 1. Label, 2. Valor unico, 3. Valor padrao
    produtos = st.multiselect('Selecione os produtos', dados['Produto'].unique(), dados['Produto'].unique())
with st.sidebar.expander('Categoria do produto'):
    categoria = st.multiselect('Selecione a categoria do produto', dados['Categoria do Produto'].unique(), dados['Categoria do Produto'].unique())
with st.sidebar.expander('Preço do produto'): # 04 parametros no slider, 1. Label, 2. min, 3. max, 4, slider de intervalo
    preco = st.slider('Selecione o preço', 0, 5000, (0,5000))
with st.sidebar.expander('Frete'):
    frete = st.slider('Selecione o valor de frete', 0, 250, (0, 250))
with st.sidebar.expander('Data da compra'):  # O mínimo e máximo para o date_impute tem de ser passado dentro de uma tupla)
    data_compra = st.date_input('Selecione a data', (dados['Data da Compra'].min(), dados['Data da Compra'].max()))
with st.sidebar.expander('Vendedor'):
    vendedor = st.multiselect('Selecione o vendedor', dados['Vendedor'].unique(), dados['Vendedor'].unique())
with st.sidebar.expander('Local da compra'):
    local = st.multiselect('Selecione o local da compra', dados['Local da compra'].unique(), dados['Local da compra'].unique())
with st.sidebar.expander('Avaliação da compra'):
    avaliacao = st.slider('Selecione a avaliação', 1, 5, value = (1,5))
with st.sidebar.expander('Tipo de pagamento'):
    tipo_pagamento = st.multiselect('Selecione o tipo de pagamento', dados['Tipo de pagamento'].unique(), dados['Tipo de pagamento'].unique())
with st.sidebar.expander('Quantidade de parcelcas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 1, 24, (1,24))

# Aplicando as filtragens do sidebar do streamlit ao dataframe que é exibido
# nome_var in @variavel do filtro and \ para saltar para outro (quando multiselect); 
# @variavel do filtro[0] <= nome_var (com crases caso tenha espacos no nome) <= @variavel do filtro[1] quando slider

query = '''
Produto in @produtos and \
`Categoria do Produto` in @categoria and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local and \
@avaliacao[0] <= `Avaliação da compra` <= @avaliacao[1] and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]

'''

# Acionando os filtros
dados_filtrados = dados.query(query)        # Para o sidebar
dados_filtrados = dados_filtrados[colunas]  # Para o topo do dataframe (selecionar as colunas)

# Mostrando o dataframe
st.dataframe(dados_filtrados)

# Inserindo um texto sobre as colunas e linhas exibidas
st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas :blue[{dados_filtrados.shape[1]}] colunas.')



# Configurações gerais para download

st.markdown('')

coluna1, coluna2 = st.columns(2)

with coluna1:
    st.markdown('**Download da tabela** :file_folder:')
    st.download_button('Formato em CSV :page_facing_up:', data = converte_csv(dados_filtrados), file_name = 'tabela.csv', mime = 'text/csv', on_click = mensagem_sucesso)  
    st.download_button('Formato em XSLS :page_with_curl:', data=converte_xlsx(dados_filtrados), file_name='tabela.xlsx',
                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', on_click=mensagem_sucesso)

# Formatação dando ao usuário opção de renomear o arquivo

# Inserindo um texto para as opções de download
# st.markdown('Escreva um nome para o arquivo')

# with coluna1:
#     nome_arquivo = st.text_input('', label_visibility='collapsed', value = 'dados em csv')  # O label é dispensável uma vez que ja usamos um markdown
#     nome_arquivo += '.csv'    
#     st.download_button('Download da tabela em CSV', data = converte_csv(dados_filtrados), file_name = 'dados.csv', mime = 'text/csv', on_click = mensagem_sucesso)                                                                 # Garantindo que o arquivo sairá com o.csv ao final

# with coluna2:
#     nome_arquivo = st.text_input('', label_visibility='collapsed', value = 'dados em xslx')  # O label é dispensável uma vez que ja usamos um markdown
#     nome_arquivo += '.xlsx'   
#     st.download_button('Download da tabela em XSLS', data=converte_xlsx(dados_filtrados), file_name='dados.xlsx',
#                        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', on_click=mensagem_sucesso)
    
