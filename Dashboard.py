import streamlit as st
import pandas as pd
import requests
import plotly.express as px

# Configurações de exibição para o usuário

st.set_page_config(page_title='Dashboard de vendas', page_icon=':shopping_trolley:',
                   initial_sidebar_state = 'collapsed', layout = 'wide',
                   menu_items={'About': 'Desenvolvido por José Alves Ferreira Neto - jose.alvesfn@gmail.com ',
                               'Report a bug': 'https://www.alura.com.br/',
                               'Get help': 'https://www.linkedin.com/in/jos%C3%A9-alves-ferreira-neto-1bbbb8192/'})


## ------------------------ FUNCOES ------------------------ ##

# Funcoes que formatam números, tanto para monetário quanto para contagem
## Funcao para valores de cabeçalho das colunas
def formata_numero(valor, prefixo = ''):
    for unidade in ['', 'mil', 'milhões']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor = valor / 1000

## Funcao para valores dos rótulos dos gráficos
def formata_numero_v2(valor, prefixo=''):
    valor_formatado = f'{prefixo} {valor:.2f}'
    return valor_formatado


st.title('DASHBOARD DE VENDAS :shopping_trolley:')

## ------------------------ SOLICITACOES / FILTRAGENS ------------------------ ##

# Solicitando dados da API, transformando a requisição num JSON e já transformando num dict para um dataframe, além de outras tratamentos
url = 'http://labdados.com/produtos'

# Há como 'filtrar alguns dados antes mesmo de concluir o consumo da API

## Filtragem de regiões
regioes = ['Brasil', 'Centro-Oeste', 'Nordeste', 'Norte', 'Sudesde', 'Sul']
st.sidebar.title('Filtros')
regiao = st.sidebar.selectbox('Regioes', regioes)

if regiao == 'Brasil':
    regiao = ''

## Filtragem de anos, aqui usa-se o checkbox, como padrao um boolean
todos_os_anos = st.sidebar.checkbox('Dados de todo o período', value = True)
if todos_os_anos: # Aqui por hora definimos o dafalt acima como True, ou seja, não ocorrerá filtragem
    ano = ''
else:
    ano = st.sidebar.slider('Ano', 2020, 2023) # Três parâmetros, sendo 1. Label, 2. Min, 3. Max

## Passando para a URL o que se deseja já na filtragem de url

query_string = {'regiao': regiao.lower(), 'ano': ano}

## Configurando a importação da API
response = requests.get(url, params = query_string)
dados = pd.DataFrame.from_dict(response.json())
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'], format = '%d/%m/%Y')  # Transformando os valores str do campo Data da Compra em tipo datetime

## Filtragem para os vendedores

filtro_vendedores = st.sidebar.multiselect('Vendedores', dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]

## ------------------------ TABELAS ------------------------ ##

# ------ Tabelas de RECEITAS ------ #

# Aqui se procura a soma dos preços das vendas por Estado, portando fazer um groupby, depois deixar as colunas de interesse e realizar um merge entre esse df das colunas de 
# interesse e o dataframe agrupado, sendo a esquerda se mantem o dataframe do drop_duplicates e a direira o indice do douppby anterior
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset = 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(receita_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)


### Criando tabelas para a receita por mês do ano
receita_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].sum().reset_index()
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mês'] = receita_mensal['Data da Compra'].dt.month_name()

### Criando tabela para receita por categoria
receita_categorias = dados.groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço', ascending=False)



# ------ Tabelas de VENDAS ------ #
vendas_estados = dados.groupby('Local da compra')[['Preço']].count()
vendas_estados = dados.drop_duplicates(subset= 'Local da compra')[['Local da compra', 'lat', 'lon']].merge(vendas_estados, left_on='Local da compra', right_index=True).sort_values('Preço', ascending=False)

### Criando tabelas para as vendas por mês do ano
venda_mensal = dados.set_index('Data da Compra').groupby(pd.Grouper(freq = 'M'))['Preço'].count().reset_index()
venda_mensal['Ano'] = venda_mensal['Data da Compra'].dt.year
venda_mensal['Mês'] = venda_mensal['Data da Compra'].dt.month_name()

### Criando tabela para vendas por categoria
vendas_categorias = dados.groupby('Categoria do Produto')[['Preço']].count().sort_values('Preço', ascending=False)

# ------ Tabelas de VENDEDORES ------ #

vendedores = pd.DataFrame(dados.groupby('Vendedor')['Preço'].agg(['sum', 'count']))



## ------------------------ GRÁFICOS------------------------ ##

### MAPA geral de receitas
fig_mapa_receita = px.scatter_geo(receita_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Receita por Estado')


# Zoom no BR
fig_mapa_receita.update_geos(
    visible=False,
    resolution=110,
    showcountries=True,
    countrycolor="darkgray",
    countrywidth=1.5,
    showsubunits=True,
    subunitcolor="lightgray"
)

fig_mapa_receita.update_geos(
    lataxis_range=[-35, 5],
    lonaxis_range=[-80, -30]
)

### MAPA geral de vendas
fig_mapa_vendas = px.scatter_geo(vendas_estados,
                                  lat = 'lat',
                                  lon = 'lon',
                                  scope = 'south america',
                                  size = 'Preço',
                                  template = 'seaborn',
                                  hover_name = 'Local da compra',
                                  hover_data = {'lat': False, 'lon': False},
                                  title = 'Vendas por Estado')

# Zoom no BR
fig_mapa_vendas.update_geos(
    visible=False,
    resolution=110,
    showcountries=True,
    countrycolor="darkgray",
    countrywidth=1.5,
    showsubunits=True,
    subunitcolor="lightgray"
)

fig_mapa_vendas.update_geos(
    lataxis_range=[-35, 5],
    lonaxis_range=[-80, -30]
)

### Gráfico de LINHAS para receitas mensais
fig_receita_mensal = px.line(receita_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers=True,
                             range_y = (0, receita_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Receita Mensal')

fig_receita_mensal.update_layout(yaxis_title = 'Receita') # Necessário realizar isso por conta que o eixo y está como 'Preço'

### Gráfico de LINHAS para vendas mensais
fig_venda_mensal = px.line(venda_mensal,
                             x = 'Mês',
                             y = 'Preço',
                             markers=True,
                             range_y = (0, venda_mensal.max()),
                             color = 'Ano',
                             line_dash = 'Ano',
                             title = 'Vendas Mensais')

fig_venda_mensal.update_layout(yaxis_title = 'Vendas') # Necessário realizar isso por conta que o eixo y está como 'Preço'

### Gráfico de BARRAS para receita dos estados

fig_receita_estados = px.bar(receita_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True,     # Parâmetro para inserir o valor no alto da barra (rótulo de dado)
                             title = 'Top Estados com maior receita')

fig_receita_estados.update_layout(yaxis_title = 'Receita') # Necessário realizar isso por conta que o eixo y está como 'Preço'
fig_receita_estados.update_yaxes(tickformat=".2s")  # Formatar os rótulos do eixo y com duas casas decimais


### Gráfico de BARRAS para vendas dos estados

fig_vendas_estados = px.bar(vendas_estados.head(),
                             x = 'Local da compra',
                             y = 'Preço',
                             text_auto=True,     # Parâmetro para inserir o valor no alto da barra (rótulo de dado)
                             title = 'Top Estados com maiores vendas')

fig_vendas_estados.update_layout(yaxis_title = 'Vendas') # Necessário realizar isso por conta que o eixo y está como 'Preço'
#fig_vendas_estados.update_yaxes(tickformat=".2s")  # Formatar os rótulos do eixo y com duas casas decimais


### Gráfico de BARRAS para categoria dos produtos por RECEITA (como só há dois campos nessa tabela, o plotly imediatamente reconhece)
fig_receita_produtos = px.bar(receita_categorias,
                              text_auto=True,     # Parâmetro para inserir o valor no alto da barra (rótulo de dado)
                              title = 'Receita por categoria de produto')

fig_receita_produtos.update_layout(yaxis_title = 'Receita') # Necessário realizar isso por conta que o eixo y está como 'Preço'
fig_receita_produtos.update_yaxes(tickformat=".2s")  # Formatar os rótulos do eixo y com duas casas decimais

### Gráfico de BARRAS para categoria dos produtos por VENDA (como só há dois campos nessa tabela, o plotly imediatamente reconhece)
fig_vendas_produtos = px.bar(vendas_categorias,
                              text_auto=True,     # Parâmetro para inserir o valor no alto da barra (rótulo de dado)
                              title = 'Vendas por categoria de produto')

fig_vendas_produtos.update_layout(yaxis_title = 'Receita') # Necessário realizar isso por conta que o eixo y está como 'Preço'
#fig_vendas_produtos.update_yaxes(tickformat=".2s")  # Formatar os rótulos do eixo y com duas casas decimais


## ------------------------ VISUALIZAÇÕES NO STREAMLIT ------------------------ ##

### Incluindo as métricas, estabelecendo as colunas para visualização, estabelcendo seções no dashboard

aba1, aba2, aba3 = st.tabs(['Receita', 'Quantidade de Vendas', 'Vendedores'])


with aba1:  # Aba de RECEITAS
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Somamos todas as vendas por aqui!')
        st.plotly_chart(fig_mapa_receita, use_container_width=True)
        # st.markdown('Mapa brasileiro com zonas de maior receita')
        st.plotly_chart(fig_receita_estados, use_container_width=True)
        
    with coluna2:    
        st.metric(f'Quantidade de vendas:', formata_numero(dados.shape[0]), help='Quantidade de vendas que nosso time realizou!')
        st.plotly_chart(fig_receita_mensal, use_container_width=True)
        st.plotly_chart(fig_receita_produtos, use_container_width=True)

with aba2:  # Aba de VENDAS
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Somamos todas as vendas por aqui!')
        st.plotly_chart(fig_mapa_vendas, use_container_width=True)
        st.plotly_chart(fig_vendas_estados, use_container_width=True)
        
    with coluna2:    
        st.metric(f'Quantidade de vendas:', formata_numero(dados.shape[0]), help='Quantidade de vendas que nosso time realizou!')
        st.plotly_chart(fig_venda_mensal, use_container_width=True)
        st.plotly_chart(fig_vendas_produtos, use_container_width=True)


with aba3:  # Aba de vendedores
    qtd_vendedores = st.number_input('Quantidade de vendedores',2 , 10, 5)
    coluna1, coluna2 = st.columns(2)
    with coluna1:
        st.metric('Receita', formata_numero(dados['Preço'].sum(), 'R$'), help='Somamos todas as vendas por aqui!')
        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores),  # Como se usa um input, é preciso construir o grafico dentro da coluna
                                        x = 'sum',
                                        y = vendedores[['sum']].sort_values('sum', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title = f'TOP {qtd_vendedores} vendedores (por receita)')
        fig_receita_vendedores.update_layout(yaxis_title = 'Nome do vendedor')                              
        st.plotly_chart(fig_receita_vendedores)
       
    with coluna2:    
        st.metric(f'Quantidade de vendas:', formata_numero(dados.shape[0]), help='Quantidade de vendas que nosso time realizou!')
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores), # Como se usa um input, é preciso construir o grafico dentro da coluna
                                        x = 'count',
                                        y = vendedores[['count']].sort_values('count', ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title = f'TOP {qtd_vendedores} vendedores (por vendas)')
        fig_vendas_vendedores.update_layout(yaxis_title = 'Nome do vendedor')
        st.plotly_chart(fig_vendas_vendedores)
        

# Exibir a tabela (o dataframe em si)
# st.dataframe(dados)

