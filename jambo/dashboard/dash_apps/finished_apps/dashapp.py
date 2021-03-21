import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://codepen.io/amyoshino/pen/jzXypZ.css']

# app = DjangoDash('SimpleExample', external_stylesheets=external_stylesheets)
app = DjangoDash('dash_integration_id', external_stylesheets=external_stylesheets)

# import data
conn_str = 'sqlite:////Users/erickamau/Library/Mobile Documents/com~apple~CloudDocs/Work/projects/jamboml/identifier.sqlite'
df = pd.read_sql_table('eda', conn_str)

keys = [pair for pair, df in df.groupby(['hour'])]

app.css.append_css({
    "external_url": external_stylesheets
})
app.layout = html.Div(
    html.Div([
        # Adding one extra Div
        html.Div([
            html.H1(children='Jambo Store'),
            html.H3(children='Here are your latest insights'),
            html.Div(children='Dash: Python framework to build web application'),
        ], className='row'),
        html.Div([
            html.Div([
                dcc.Graph(
                    id='bar-chart',
                    figure={
                        'data': [
                            {'x': df['month'], 'y': df['Gross'], 'hue': df['year'], 'type': 'bar', 'name': 'SF'},
                        ],
                        'layout': {
                            'title': 'Best month for Sales'
                        }
                    }
                ),
            ], className='six columns'),
            # Adding one more app/component
            html.Div([
                dcc.Graph(
                    id='line-chart',
                    figure={
                        'data': [
                            {'x': keys, 'y': df.groupby(['hour']).count()['Count'], 'type': 'line', 'name': 'SF'},
                        ],
                        'layout': {
                            'title': 'Best time for sales'
                        }
                    }
                )
            ], className='six columns')
        ], className='row')
    ])
)
if __name__ == '__main__':
    app.run_server(8052, debug=False)
