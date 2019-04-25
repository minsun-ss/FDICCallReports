import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

munidata = pd.read_csv('munidata.csv').set_index('Financial Institution Name')
munitotal = pd.read_csv('munitotal.csv').set_index('CallDate')

# build the dict for the title name
quarter_names = {'Q1': 'First Quarter', 'Q2': 'Second Quarter', 'Q3': 'Third Quarter', 'Q4': 'Fourth Quarter'}

# launch app
app = dash.Dash(__name__)
app.title = 'Municipal Loans Held By Banks'
server = app.server

def serve_layout():
    return html.Div(children=[
            html.H5(children='Municipal Loans', id='graph_title'),
            html.Button('Press Here to Advance a Quarter', id='keypress'),
            dcc.Graph(id='muni_total_graph', ),


            dcc.Graph(
                id='muni_graph',
            ),

            html.Div(id='storage_value', style={'display': 'none'})
        ])

app.layout = serve_layout

@app.callback(
    Output('storage_value', 'children'),
    [Input('keypress', 'n_clicks')]
)
def update_data(quarter_update):
    return quarter_update

# the interactive section
@app.callback(
    [Output('muni_graph', 'figure'), Output('muni_total_graph', 'figure'), Output('graph_title', 'children')],
    [Input('keypress', 'n_clicks'),
     Input('storage_value', 'children')
     ])
def update_figure(selected_press, storage_value):

    # determines quarter based on stored value
    if storage_value is None:
        current_quarter_loc = 0
    else: current_quarter_loc = storage_value % len(munidata.columns.values)

    current_quarter = munidata.columns.values[current_quarter_loc]

    # re-sort the muni values and maybe just get top 50
    munidata.sort_values(by=current_quarter, ascending=True, inplace=True)
    subset = munidata.tail(50).copy()

    # build the top 50 bar
    bar_figure={
            'data': [
                go.Bar(
                    y=subset.index,
                    x=subset[current_quarter].values,
                    name=current_quarter,
                    hoverinfo='skip',
                    orientation='h'
                ),
            ],
            'layout': go.Layout(
                height=900,
                xaxis={'mirror': 'allticks', 'side': 'top', 'range': [0, 25000],
                       'title': go.layout.xaxis.Title(text='$ millions'),},
                margin=go.layout.Margin(
                    l=400,
                    t=40
                ),
            )
        }

    # set all colors to gray, then highlight the approprate color
    munitotal['Color'] = 'rgba(204,204,204,1)'
    munitotal.loc[current_quarter, 'Color'] = 'rgba(222,45,38,0.8)'

    # build the total bar
    total_figure = {
        'data': [go.Bar(
        y=munitotal['ALL BANKS'].values,
        x=munitotal.index,
        name='All',
        hoverinfo='skip',
        marker=dict(
            color=munitotal['Color'].values
        ),
        ),],
        'layout': go.Layout(
            height=150,
            margin=go.layout.Margin(
                l=400,
                t=40),
            xaxis=dict(
                ticklen=8
            )
        )
    }

    new_title='Municipal Loans Held by Top 50 Banks: {} {} - see https://www.stuffofminsun.com'.format(quarter_names[current_quarter[-2:]], current_quarter[:4])

    return bar_figure, total_figure, new_title





if __name__ == '__main__':
    app.run_server(debug=True)