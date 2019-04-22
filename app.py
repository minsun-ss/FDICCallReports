import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go

munidata = pd.read_csv('munidata.csv').set_index('Financial Institution Name')
munidata.sort_values(by='2001Q1', ascending=True, inplace=True)

# build the dict for the dropdowns
dropdown = [{'label': i, 'value': i} for i in munidata.columns.values]

# cycle through the location of the quarter
current_quarter_location = 0

# launch app
app = dash.Dash(__name__)
app.title = 'Munis!!!!'
server = app.server

def serve_layout():
    return html.Div(children=[
            html.H5(children='Municipal Loans'),

            html.Button('Press Here to Advance a Quarter', id='keypress'),

            dcc.Graph(
                id='muni_graph',
            ),
        ])


app.layout = serve_layout

# the interactive section
@app.callback(
    [Output('muni_graph', 'figure')],
##    [Input('quarter_menu', 'value'),
     [Input('keypress', 'n_clicks')]
)
def update_figure(selected_press):
    global current_quarter_location
    current_quarter = munidata.columns.values[current_quarter_location]

    # this moves to the next one in the stack but isn't used
    current_quarter_location += 1

    if current_quarter_location == len(munidata.columns.values):
        current_quarter_location = 0

    # check to see if selected_asset is empty
    #selected_quarter = selected_asset
    #if selected_quarter is None:
    #    selected_quarter = '2001Q1'

    # re-sort the muni values and maybe just get top 50
    munidata.sort_values(by=current_quarter, ascending=True, inplace=True)
    subset = munidata.tail(50).copy()

    # am not sure why the hell this needs ot be returned as a tuple/list instead of just a dict like in the previous
    # visualization, but.... well, whatever works
    a_figure=[{
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
                title= go.layout.Title(text=current_quarter,x=.2),
                height=900,
                xaxis={'mirror': 'allticks', 'side': 'top', 'range': [0, 5], 'type': 'log', 'title': go.layout.xaxis.Title(
                    text='$ millions'
                )},
                margin=go.layout.Margin(
                    l=400,
                    t=40
                ),
            )
        }]

    return a_figure

'''        dcc.Dropdown(
        options=dropdown,
        id='quarter_menu',
        placeholder='Current Quarter',
        clearable='False',
        searchable='True'
    ), 
    dcc.Slider(
        id = 'quarter_slider',
        min = 0,
        max = len(munidata.columns.values)-1,
        marks = {int(np.where(munidata.columns.values == i)[0][0]): i for i in munidata.columns.values}
    ),'''



if __name__ == '__main__':
    app.run_server(debug=True)