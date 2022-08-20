app.layout = dbc.Container(
    dbc.Row([
        dbc.Col([
            html.Div([
                html.Img(id='logo', src=app.get_asset_url("logo_dark.png"), height=50),
                html.H5("Evolução da COVID-19 no Brasil"),
                dbc.Button("BRASIL", color='primary', id='location-button', size='lg')
            ], style={}),
            html.P('Informe a data na qual deseja obter informações:', style={'margin-top': "40px"}),
            html.Div(id="div-test", children=[
                dcc.DatePickerSingle(
                    id='date-picker',
                    min_date_allowed=df_brasil['data'].min(),
                    max_date_allowed=df_brasil['data'].max(),
                    initial_visible_month=df_brasil['data'].min(),
                    date=df_brasil['data'].max(),
                    display_format='MMMM D, YYYY',
                    style={'border': '0px solid black'}
                )
            ]),
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Span('Casos Recuperados'),
                        html.H3(style={'color': '#adfc92'}, id='casos-recuperados-text'),
                        html.Span('Em acompanhamento'),
                        html.H5(id='em-acompanhamento-text'),
                    ])
                ], color='light', outline=True, style={'margin-top': '10px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF'})
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Span('Casos Confirmados Totais'),
                        html.H3(style={'color': '#a38fd6'}, id='casos-confirmados-text'),
                        html.Span('Novos Casos na Data'),
                        html.H5(id='novos_casos-text'),
                    ])
                ], color='light', outline=True, style={'margin-top': '10px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF'})
            ], md=4),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Span('Obitos Confirmados'),
                        html.H3(style={'color': '#DF2935'}, id='obitos-text'),
                        html.Span('Obitos na Data'),
                        html.H5(id='obitos-na-data-text'),
                    ])
                ], color='light', outline=True, style={'margin-top': '10px',
                                    'box-shadow': '0 4px 4px 0 rgba(0, 0, 0, 0.15), 0 4px 20px 0 rgba(0, 0, 0, 0.19)',
                                    'color': '#FFFFFF'})
            ], md=4)
        ]),
            html.Div([
                html.P('Selecione que tipo de dado deseja visualizar:', style={'margin-top': '25px'}),
                dcc.Dropdown(
                                id="location-dropdown",
                                options=[{"label": j, "value": i}
                                    for i, j in select_columns.items()
                                ],
                                value="casosNovos",
                                style={"margin-top": "10px"}
                            ),
                dcc.Graph(id="line-graph", figure=fig2)
            ]),
            
        ], md=6, style={'padding': '25px', 'background-color': '#242424'}),
        dbc.Col([
            dcc.Loading(id='loading-1', type='default',
            children=[
                dcc.Graph(id="choropleth-map", figure=fig, style={'height': '100vh', 'margin-right': '10px'})
                ]
            )
        ], md=6)
    ])
, fluid=True)