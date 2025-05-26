import streamlit as st
import requests
import pandas as pd
import plotly.express as px

#========================================================
##CONFIGS 
page_title = 'DASHBOARD DE VENDAS'
page_icon = '🛒'
layout = 'wide'
st.set_page_config(page_title=page_title, page_icon=page_icon, layout='wide')


#========================================================
#FUNÇÕES
def formata_numero(valor,prefixo=''):
    for unidade in ['','mil']:
        if valor < 1000:
            return f'{prefixo} {valor:.2f} {unidade}'
        valor = valor / 1000
    return f'{prefixo} {valor:.2f} milhões'


#========================================================
##CONEXÃO
#URL dos dados
url = 'https://labdados.com/produtos'
regioes = ['Brasil','Centro-oeste','Nordeste','Sudeste','Sul','Norte']

#Criando sidebar com filtros
st.sidebar.title('Filtros')
###Região
regiao = st.sidebar.selectbox('Região',regioes)
if regiao == 'Brasil':
    regiao = ''
###Ano
todos_anos = st.sidebar.checkbox('Dados de todo o período',value = True)
if todos_anos:
    ano = ''
else:
    ano = st.sidebar.slider('Ano',2020,2023)

query_string = {'regiao':regiao.lower(),'ano':ano}

#Pepagem dos dados da API
response = requests.get(url,params=query_string)
#Converte dados em json e o json em um dataframe
dados = pd.DataFrame.from_dict(response.json())
#Formatando data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'],format='%d/%m/%Y')

###Vendedores
filtro_vendedores = st.sidebar.multiselect('Vendedores',dados['Vendedor'].unique())
if filtro_vendedores:
    dados = dados[dados['Vendedor'].isin(filtro_vendedores)]


#========================================================
###TABELAS

##TABELAS DE RECEITA
#tabela de vendas por estado
receita_estados = dados.groupby('Local da compra')[['Preço']].sum()
receita_estados = dados.drop_duplicates(subset=['Local da compra'])[['Local da compra','lat','lon']]\
                    .merge(receita_estados,left_on='Local da compra',right_index=True)\
                    .sort_values(by='Preço',ascending=False)

#tabela de receita mensal por data
receita_mensal = dados.set_index('Data da Compra')\
                    .groupby(pd.Grouper(freq='M'))[['Preço']].sum().reset_index()
#add colunas
receita_mensal['Ano'] = receita_mensal['Data da Compra'].dt.year
receita_mensal['Mes'] = receita_mensal['Data da Compra'].dt.month_name()

#tabela receita por categoria
receita_categorias = dados\
                        .groupby('Categoria do Produto')[['Preço']].sum().sort_values('Preço',ascending=False)

##TABELAS DE QTD DE VENDAS
#tabela quantidade de vendas por estado
quantidade_estados = dados\
                        .groupby('Local da compra')\
                        .agg(
                                Quantidade_de_vendas=('Local da compra', 'size'),
                                lat=('lat', 'first'),  # or 'mean' if there are multiple coordinates per state
                                lon=('lon', 'first')   # or 'mean' if there are multiple coordinates per state
                            )\
                        .reset_index()\
                        .sort_values('Quantidade_de_vendas', ascending=False)
#tabela quantidade de vendas por data
quantidade_mensal = dados\
                        .groupby(pd.Grouper(key='Data da Compra', freq='M'))\
                        .agg(
                                Quantidade_de_vendas_mensal=('Data da Compra', 'size')
                            )\
                        .reset_index()
#add colunas
quantidade_mensal['Ano'] = quantidade_mensal['Data da Compra'].dt.year
quantidade_mensal['Mes'] = quantidade_mensal['Data da Compra'].dt.month_name()

#tabela qtd de vendas por categoria
quantidade_categorias = dados\
                        .groupby('Categoria do Produto')\
                        .agg(
                            Quantidade_de_vendas_por_cat=('Categoria do Produto', 'size')
                        )\
                        .sort_values('Quantidade_de_vendas_por_cat',ascending=False)

##TABELAS DE VENDEDORES
vendedores = pd.DataFrame(dados\
                          .groupby('Vendedor')['Preço']\
                        .agg(
                            ['sum','count']
                        ))

##GRÁFICOS
###Gráficos de Receita
fig_mapa_receita = px.scatter_geo(receita_estados,
                                lat='lat',
                                lon = 'lon',
                                scope='south america',
                                size = 'Preço',
                                template ='seaborn',
                                hover_name='Local da compra',
                                hover_data={'lat':False,'lon':False},
                                title= 'Receita por estado')

fig_receita_mensal = px.line(receita_mensal,
                            x='Mes',
                            y='Preço',
                            markers=True,
                            range_y= (0,receita_mensal.max()),
                            color='Ano',
                            line_dash='Ano',
                            title='Receita mensal')
fig_receita_mensal.update_layout(yaxis_title='Receita')

fig_receita_estados = px.bar(receita_estados.head(),
                            x='Local da compra',                                
                            y='Preço',
                            text_auto=True,
                            title='Top estados(receitas)')
fig_receita_estados.update_layout(yaxis_title='Receita')

fig_receita_categorias = px.bar(receita_categorias.head(),
                                text_auto=True,
                                title='Top categorias(receitas)')
fig_receita_categorias.update_layout(yaxis_title='Receita')

###Gráficos de Quantidade de Vendas
fig_mapa_qtdVendas = px.scatter_geo(quantidade_estados,
                                lat='lat',
                                lon = 'lon',
                                scope='south america',
                                size = 'Quantidade_de_vendas',
                                template ='seaborn',
                                hover_name='Local da compra',
                                hover_data={'lat':False,'lon':False},
                                title= 'Vendas por estado')

fig_qtdVendas_mensal = px.line(quantidade_mensal,
                            x='Mes',
                            y='Quantidade_de_vendas_mensal',
                            markers=True,
                            range_y= (0,quantidade_mensal.max()),
                            color='Ano',
                            line_dash='Ano',
                            title='Quantidade de vendas mensal')

fig_qtdVendas_estados = px.bar(quantidade_estados.head(),
                            x='Local da compra',                                
                            y='Quantidade_de_vendas',
                            text_auto=True,
                            title='Top estados(qtd)')

fig_qtdVendas_categorias = px.bar(quantidade_categorias.head(),
                                text_auto=True,
                                title='Top categorias(qtd)')

#========================================================
##VISUALIZAÇÃO DE DADOS
#Add titulo
st.title("DASHBOARD DE VENDAS :shopping_trolley:")

#ABAS
aba1,aba2,aba3 = st.tabs(['Receita','Quantidade de vendas','Vendedores'])
with aba1:
    #COLUNAS
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita",formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_receita,use_container_width=True)
        st.plotly_chart(fig_receita_estados,use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas",formata_numero(dados.shape[0]))
        st.plotly_chart(fig_receita_mensal,use_container_width=True)
        st.plotly_chart(fig_receita_categorias,use_container_width=True)
with aba2:
    #COLUNAS
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita",formata_numero(dados['Preço'].sum(),'R$'))
        st.plotly_chart(fig_mapa_qtdVendas,use_container_width=True)
        st.plotly_chart(fig_qtdVendas_estados,use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas",formata_numero(dados.shape[0]))
        st.plotly_chart(fig_qtdVendas_mensal,use_container_width=True)
        st.plotly_chart(fig_qtdVendas_categorias,use_container_width=True)
with aba3:
    #ITERAÇÃO
    qtd_vendedores =  st.number_input('Quantidade de vendedores',min_value=2,max_value=10,value=5)
    #COLUNAS
    coluna1,coluna2 = st.columns(2)
    with coluna1:
        st.metric("Receita",formata_numero(dados['Preço'].sum(),'R$'))

        fig_receita_vendedores = px.bar(vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores),
                                        x='sum',
                                        y = vendedores[['sum']].sort_values('sum',ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores(receita)')
        st.plotly_chart(fig_receita_vendedores,use_container_width=True)
    with coluna2:
        st.metric("Quantidade de vendas",formata_numero(dados.shape[0]))
    
        fig_vendas_vendedores = px.bar(vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores),
                                        x='count',
                                        y = vendedores[['count']].sort_values('count',ascending=False).head(qtd_vendedores).index,
                                        text_auto=True,
                                        title=f'Top {qtd_vendedores} vendedores(qtdVendas)')
        st.plotly_chart(fig_vendas_vendedores,use_container_width=True)

#DATAFRAME DE VENDAS
#st.dataframe(dados)

