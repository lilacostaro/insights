import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go

import numpy as np
import pandas as pd
import json
import os

import psycopg2
import yaml


localdir = os.path.dirname(__file__)
with open(f'{localdir}/env.yaml', 'r') as yaml_file:
    env = yaml.safe_load(yaml_file)
    
print(env['DADOS_AWS']['username'])
host = env['DADOS_AWS']['host']
username = env['DADOS_AWS']['username']
password = env['DADOS_AWS']['password']
database = env['DADOS_AWS']['database']
port = env['DADOS_AWS']['port']

conn = psycopg2.connect(host=host, 
                 port=port, 
                 user=username, 
                 password=password, 
                 database=database, 
                 options="-c search_path=collect_lite,public")

def get_process_data(conn):

    query = """
        select
            *
        from 
        sales_complete
    """

    df = pd.read_sql_query(query, conn)

    df['transaction_date'] = df['transaction_date'].astype(str)
    df['transaction_time'] = df['transaction_time'].astype(str)

    df['full_datetime'] = pd.to_datetime(df['transaction_date'] + ' ' + df['transaction_time'])
    df['week_of_year'] = df['full_datetime'].dt.isocalendar().week.astype(int)
    df['id_day_of_week'] = df['full_datetime'].dt.dayofweek
    df['day_of_week'] = df['full_datetime'].dt.day_name()
    df['hour_sale'] = df['full_datetime'].dt.strftime('%H').astype(int)


    return df

df = get_process_data(conn)

conn.close()

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

Vendas_por_dia = df.groupby('transaction_date').sum().reset_index()

fig_1 = px.line(Vendas_por_dia, x='transaction_date', y='full_price', title='Faturamento por dia', labels={
                     "full_price": "Faturamento"
                 })

faturamento_por_semana = df[['full_price', 'week_of_year']].groupby(['week_of_year']).sum().reset_index().sort_values('week_of_year')


fig_2 = px.bar(faturamento_por_semana, x='week_of_year', y='full_price', title='Faturamento por semana', labels={
                     "full_price": "Faturamento"
                 })

faturamento_por_hora = df[['hour_sale','full_price']].groupby(['hour_sale']).sum().reset_index()

fig_3 = px.bar(faturamento_por_hora, x='hour_sale', y='full_price', title='Faturamento total por hora', labels={
                     "full_price": "Faturamento"
                 })

date_by_customer = df[['card_id', 'full_datetime']].groupby(['card_id']).max().reset_index()

last_date = date_by_customer['full_datetime'].max()

date_by_customer['days_since_last_buy'] = (last_date - date_by_customer['full_datetime']).dt.days

days_to_churn = 7

date_by_customer['churned'] = date_by_customer['days_since_last_buy'].apply(lambda x: 'Sim' if x > 15 else 'Nao')

churn_cliente = date_by_customer.groupby('churned').count().reset_index()

# print(f'{churn_cliente[churn_cliente['churned']=='Sim']['card_id']:.2%} não retornaram nos ultimos {days_to_churn} dias.')

fig_4 = px.pie(churn_cliente, values='card_id', names='churned')


count_by_customer = df.groupby('card_id').count().reset_index()[['card_id', 'transaction_id']]

recorrente_cliente = len(count_by_customer[count_by_customer['transaction_id'] > 1]) / len(count_by_customer)
# print(f'{recorrente_cliente:.2%} dos cliente compraram mais de um pedido em abril de cartão.')

atracao_cliente = df.sort_values(['transaction_date']).drop_duplicates('card_id', keep='first')
atracao_cliente = atracao_cliente[['transaction_date', 'week_of_year']].groupby('week_of_year').count()
atracao_cliente.rename(columns={'transaction_id': 'new_clients'}, inplace=True)
taxa_atracao = -1 + (atracao_cliente.iloc[len(atracao_cliente) - 1, 0] / atracao_cliente.iloc[1,0])

clientes_totais = atracao_cliente.transaction_date.sum()

faturamento_mensal = 23500

df_tipo_cartao = df.loc[ df['card_id'] != 0,['transaction_id', 'forma_pagamento']].copy()
df_tipo_cartao = df_tipo_cartao.groupby('forma_pagamento').count().reset_index()
top_tipo_cartao = df_tipo_cartao[df_tipo_cartao['transaction_id'] == df_tipo_cartao['transaction_id'].max()]

app.layout = dbc.Container([
    dbc.Row([
        html.Div([
            dbc.Col([html.Img(id='logo', src=app.get_asset_url("teamplay.png"), height=150),]),
            dbc.Col([html.H1("Statistics Lite"),]),
        ], style={'display': 'flex', 'padding': '35px'}),
    ]),
    dbc.Row([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.H3(f'{recorrente_cliente:.2%}'),
                    html.H5(id='taxa_recorrencia_dado'),
                    html.Span('Taxa de Recorrencia'),
                    html.H3(style={'color': '#adfc92'}, id='taxa_recorrencia_text'),
                    
                ])
            ], color='light', outline=True, style={'margin-top': '10px', 'margin-left': '20px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF', 'padding': '75px'}),
            dbc.Card([
                dbc.CardBody([
                    html.H3(f'{taxa_atracao:.2%}'),
                    html.H5(id='taxa_atracao_dado'),
                    html.Span('Taxa de Atração'),
                    html.H3(style={'color': '#adfc92'}, id='taxa_atracao_text'),
                    
                ])
            ], color='light', outline=True, style={'margin-top': '10px', 'margin-left': '20px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF', 'padding': '75px'}),
            dbc.Card([
                dbc.CardBody([
                    html.H3(f'{clientes_totais}'),
                    html.H5(id='clientes_totais_dado'),
                    html.Span('Total de Clientes No Mês'),
                    html.H3(style={'color': '#adfc92'}, id='clientes_totais_text'),
                    
                ])
            ], color='light', outline=True, style={'margin-top': '10px', 'margin-left': '20px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF', 'padding': '75px'}),
        ], style={'display': 'flex', 'padding': '35px', 'align-items': 'center'})
        
    ]),
    
    dbc.Row([
        html.Div([
            dbc.Card([
                dbc.CardBody([
                    html.Span(f'Que tipo de cartão mais foi usado? \n{top_tipo_cartao["forma_pagamento"].values[0]}'),
                    html.H3(style={'color': '#adfc92'}, id='dado_4'),
                    html.Span(f'{top_tipo_cartao["transaction_id"].values[0]}'),
                    html.H5(id='texto_4'),
                ])
            ], color='light', outline=True, style={'margin-top': '10px', 'margin-left': '20px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF', 'padding': '75px'}),
            dbc.Card([
                dbc.CardBody([
                    html.Span('Faturamento Mensal'),
                    html.H3(style={'color': '#adfc92'}, id='dado_5'),
                    html.Span(f'{faturamento_mensal}'),
                    html.H5(id='texto_5'),
                ])
            ], color='light', outline=True, style={'margin-top': '10px', 'margin-left': '20px',
                                        'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                        'color': '#FFFFFF', 'padding': '75px'}),
            dbc.Card([
                dbc.CardBody([
                    html.Span('Faturamento Mensal'),
                    html.H3(style={'color': '#adfc92'}, id='dado_6'),
                    html.Span(f'{faturamento_mensal}'),
                    html.H5(id='texto_6'),
                ])
            ], color='light', outline=True, style={'margin-top': '10px', 'margin-left': '20px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF', 'padding': '75px'}),
        ], style={'display': 'flex', 'padding': '35px', 'align-items': 'center'})
        
    ]),
    dcc.Graph(
        id='example-graph_1',
        figure=fig_1
    ),
    
    dcc.Graph(
        id='example-graph_2',
        figure=fig_2
    ),
    
    dcc.Graph(
        id='example-graph_3',
        figure=fig_3
    ),
    
    dcc.Graph(
        id='example-graph_4',
        figure=fig_4
    ),
])

# app.layout = html.Div(children=[
#     html.H1(children='Óla seu José da Padaria'),

#     html.Div(children='''
#         Statistics Lite um app desenvolvido para gerar informações sobre o seu negocio!
#     '''),

#     dcc.Graph(
#         id='example-graph_1',
#         figure=fig_1
#     ),
    
#     dcc.Graph(
#         id='example-graph_2',
#         figure=fig_2
#     ),
    
#     dcc.Graph(
#         id='example-graph_3',
#         figure=fig_3
#     ),
    
#     dcc.Graph(
#         id='example-graph_4',
#         figure=fig_4
#     ),
# ])

if __name__ == '__main__':
    app.run_server(debug=True)