'''
Vu Anh Vu - 2020
Credit to Ishan Mehta: https://medium.com/analytics-vidhya/create-a-time-series-visualization-web-dashboard-using-python-dash-e94c807e1d95
'''
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import sqlite3 as sl
import datetime


DB_NAME=None
HISTORY_THRESHOLD = 12 # hours

def init_web_dashboard(db_name):
    global DB_NAME
    DB_NAME=db_name
    print("init" + DB_NAME)

def start_web_dashboard():
    app.run_server(host= '0.0.0.0',port='8888')

def get_co2_data():
    data_query = "SELECT timestamp, co2_ppm from co2_info where timestamp> ? order by timestamp asc "
    print("query" + DB_NAME)
    with sl.connect(DB_NAME) as con:
        cur = con.cursor()
        now = datetime.datetime.now()
        cur.execute(data_query, (now - datetime.timedelta(hours=HISTORY_THRESHOLD),))
        records = cur.fetchall()
        con.commit()
    timestp=[]
    ppm=[]
    for record in records:
        timestp.append(record[0])
        ppm.append(record[1])
    data={
        "xaxis":timestp,
        "yaxis":ppm,
    }
    return data


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

ticker_name_dic = {'CO2':'CO2', 'TEMP':'Temperature', 'Humidity':'Humidity'}
options = []
for ticker in ticker_name_dic:
    options.append({'label': '{}'.format(ticker_name_dic[ticker]), 'value': ticker})

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dcc.Dropdown(
                    id='my_ticker_symbol',
                    options=options,
                    value='CO2'
                ),
                dbc.Button(
                    id='submit-button',
                    n_clicks=0,
                    children='Update',
                    color="primary",
                    block=True
                ),
            ]
        )
    ],
)

sidebar = html.Div(
    [
        html.H2("Sensors", className="display-4"),
        html.Hr(),
        controls
    ],
    style=SIDEBAR_STYLE,
)
CONTENT_STYLE = {
    "margin-left": "5rem",
    "margin-right": "5rem",
    "padding": "2rem 1rem",
}
content = html.Div(
    [
        html.H1('Air Quality Monitoring Dashboard', 
                style={'textAlign': 'center'}),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="my_close_price_graph"), 
                        width={"size": 10, "offset": 2}),
            ]
        )
    ],
    style=CONTENT_STYLE
)
@app.callback(
    Output('my_close_price_graph', 'figure'),
    [Input('submit-button', 'n_clicks')],
    [State('my_ticker_symbol', 'value')])

def update_graph(n_clicks, stock_ticker):
    graph_data = []
    co2_data = get_co2_data()
    graph_data.append({'x': co2_data["xaxis"], 'y': co2_data["yaxis"]})
    fig = {
        'data': graph_data,
        'layout': {'title': " CO2 PPM value"}
    }
    return fig


app.layout = html.Div([sidebar, content])






