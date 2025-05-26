import streamlit as st
import requests
import pandas as pd
import time

#========================================================
##FUNÇÕES
#Não precisa fazer a conversão várisa vezes
@st.cache_data 

def converte_csv(df):
     return df.to_csv(index=False).encode('utf-8')

def mensagem_sucesso():
    mensagem = 'Sucesso! :smiley:'
    sucesso = st.success(mensagem)
    time.sleep(2)
    sucesso.empty()


#========================================================
##CONFIGS 
page_title = 'DADOS BRUTOS'
page_icon = ''
layout = 'wide'
st.set_page_config(page_title=page_title, page_icon=page_icon, layout='wide')

st.title("DADOS BRUTOS :clipboard:")
#========================================================
##CONEXÃO
#URL dos dados
url = 'https://labdados.com/produtos'
#Pepagem dos dados da API
response = requests.get(url)
#Converte dados em json e o json em um dataframe
dados = pd.DataFrame.from_dict(response.json())
#Formatando data
dados['Data da Compra'] = pd.to_datetime(dados['Data da Compra'],format='%d/%m/%Y')

#========================================================
#FILTROS
with st.expander('Colunas'):
    colunas = st.multiselect(
        'Selecione as colunas',
        list(dados.columns),#opções disponíveis
        list(dados.columns)#opções default
        )

##SIDEBAR    
st.sidebar.title('Filtros')

####Produtos
with st.sidebar.expander('Nome do produto'):
     produtos =  st.multiselect('Selecione os produtos',
                                        dados['Produto'].unique(),
                                        dados['Produto'].unique())
###Categoria
with st.sidebar.expander('Categoria do produto'):
     categorias =  st.multiselect('Selecione as categorias',
                                        dados['Categoria do Produto'].unique(),
                                        dados['Categoria do Produto'].unique())
###Preço
with st.sidebar.expander('Preço do produto'):
     preco = st.slider('Selecione o preço',
                               0, #Valor mínimo
                               5000,#Valor máximo
                               (0,5000)#Poder selecionar mais de um valor
                               )
###Frete
with st.sidebar.expander('Frete do produto'):
     frete = st.slider('Selecione o frete',
                               0.0, #Valor mínimo
                               dados['Frete'].max(),#Valor máximo
                               (0.0,dados['Frete'].max())#Poder selecionar mais de um valor
                               )
###Data
with st.sidebar.expander('Data da compra'):
     data_compra = st.date_input('Selecione a data da compra',
                                 (dados['Data da Compra'].min(),
                                 dados['Data da Compra'].max())
                                 )
###Vendedor
with st.sidebar.expander('Vendedor'):
     vendedor = st.multiselect('Selecione o vendedor',
                                        dados['Vendedor'].unique(),
                                        dados['Vendedor'].unique())
###Local da compra
with st.sidebar.expander('Local da compra'):
     local = st.multiselect('Selecione o local da compra',
                                        dados['Local da compra'].unique(),
                                        dados['Local da compra'].unique())
###Avaliação da compra
with st.sidebar.expander('Avaliação da compra'):
     avaliacao = st.slider('Selecione a avaliação da compra',
                               0, #Valor mínimo
                               5,#Valor máximo
                               (0,5)#Poder selecionar mais de um valor
                               )
###Tipo de pagamento
with st.sidebar.expander('Tipo de pagamento'):
     tipo_pagamento = st.multiselect('Selecione o tipo de pagamento',
                                        dados['Tipo de pagamento'].unique(),
                                        dados['Tipo de pagamento'].unique())
###Quantidade de parcelas
with st.sidebar.expander('Quantidade de parcelas'):
    qtd_parcelas = st.slider('Selecione a quantidade de parcelas', 
                             1, 
                             24, 
                             (1,24))
##Aplicando Filtros
query = '''
Produto in @produtos and \
`Categoria do Produto` in @categorias and \
@preco[0] <= Preço <= @preco[1] and \
@frete[0] <= Frete <= @frete[1] and \
@data_compra[0] <= `Data da Compra` <= @data_compra[1] and \
Vendedor in @vendedor and \
`Local da compra` in @local and \
`Avaliação da compra` in @avaliacao and \
`Tipo de pagamento` in @tipo_pagamento and \
@qtd_parcelas[0] <= `Quantidade de parcelas` <= @qtd_parcelas[1]
'''

dados_filtrados = dados.query(query)
dados_filtrados = dados_filtrados[colunas]


#========================================================
##VISUALIZAÇÃO DE DADOS
#Add titulo
st.dataframe(dados_filtrados)

st.markdown(f'A tabela possui :blue[{dados_filtrados.shape[0]}] linhas e :blue[{dados_filtrados.shape[1]}] colunas')

#Download de Arquivo
st.markdown('Escreva um nome para o arquivo')
coluna1, coluna2 = st.columns(2)
with coluna1:
    nome_arquivo = st.text_input('',label_visibility='collapsed',value='dados_brutos')
    nome_arquivo += '.csv'
with coluna2:
    st.download_button('Fazer o download da tabela em csv',
                       data = converte_csv(dados_filtrados),
                       file_name = nome_arquivo,
                       mime='text/csv',
                       on_click=mensagem_sucesso)   
