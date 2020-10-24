# modified / enhanced from udemy dash course by jose portilla


import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime


# When this is set to true, all stock will be scaled to 100% on first day 
SCALE_TO_100 = True

def scale_to_100(some_series):
    return some_series / some_series[0]

# read in names and ids of nasdaq listed stock
nsdq = pd.read_csv('../Data/NASDAQcompanylist.csv') #   DAX_listed_companies  NASDAQcompanylist.csv
nsdq.set_index('Symbol', inplace = True)


# create static list of options that are selectable
options = []

for tic in nsdq.index:
    mydict = {}
    mydict['label'] = nsdq.loc[tic]['Name'] + ' ' + tic
    mydict['value'] = tic
    options.append(mydict)


app = dash.Dash()

app.layout = html.Div([
    html.H1('My first Stock Ticker'),
    
    # stock selection
    html.Div([    
        html.H3('Chose a stock symbol', style={'paddingRight':'30px'}),
        dcc.Dropdown(
            id = 'my-stock-picker',
            options = options,
            value = ['TSLA'], 
            multi = True
        # use inline-block such that elements are aligned next to each other without having to define columns
        )
    ], style = {'display':'inline-block', 'verticalAlign':'top', 'widht': '30%'}),
    
    # date picker
    html.Div([
        html.H3('Pick date Range'),
        dcc.DatePickerRange(
            id = 'date-picker',
            min_date_allowed = datetime(2000,1,1),
            max_date_allowed = datetime.today(),
            start_date = datetime(2020,1,1),
            end_date = datetime.today()
        )
    ], style = {'display': 'inline-block'}),

    # checklist: should this be scaled?
    html.Div([
        dcc.Checklist(
            id = 'scale',
                options=[
                    {'label': 'scale to 1?', 'value': 'scale'},
            ],
            value=['scale']
        )
    ], style = {'display': 'inline-block'}),  
    
    # submit button
    html.Div([
        html.Button(
            id = 'submit-button',
            n_clicks = 0,
            children = 'Submit',
            style = {'fontSize':24, 'marginLeft':'30px'}
        )
    ], style = {'display': 'inline-block'}),
    
    dcc.Graph(
        id = 'stock_data',
        figure = {
            'data': [
                {'x': [1,2,3], 'y': [1,3,1]}
            ], 'layout': {'title': 'default title'}
        }
    )
])


@app.callback(
    Output('stock_data', 'figure'),
    # input is submit button -> only when n_clicks change, the callback will be executed
    [Input('submit-button', 'n_clicks')],
    
    # use STATE here
    [
        State('my-stock-picker', 'value'),
        State('date-picker', 'start_date'),
        State('date-picker', 'end_date'),
        State('scale', 'value')
    ])
def update_data(n_clicks, stock_ticker, start_date, end_date, value):
    print(f'XXXXXXXXXXXXXXXX{value}')

    # cave: params are passed as strings not datetimeobjects, have to be parsed again
    start = datetime.strptime(start_date[:10], '%Y-%m-%d')
    end = datetime.strptime(end_date[:10], '%Y-%m-%d')

    traces = []
    for tic in stock_ticker:
        my_df = web.DataReader(tic,'yahoo',start,end)
        if 'scale' in value:
            y = scale_to_100(my_df.Close)
        else:
            y = my_df.Close
        traces.append({'x': my_df.index, 'y': y, 'name': tic})
    
    fig = {
        'data': traces,
        'layout': {'title': stock_ticker}}
    return fig

if __name__ == '__main__':
    app.run_server(port=8054)
