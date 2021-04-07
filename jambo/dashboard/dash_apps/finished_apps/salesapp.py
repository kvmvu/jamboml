from datetime import date

import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css'
]

app = DjangoDash('sales')

'''import data'''
conn_str = 'sqlite:////Users/erickamau/Library/Mobile Documents/com~apple~CloudDocs/Work/projects/jamboml/identifier.sqlite'
# sales
df = pd.read_sql_table('eda', conn_str)
# inventory
inv_df = pd.read_sql_table('inventory_clean', conn_str)

'''dataframe operations'''
# new sales calculation
daily_sales = df.groupby(by='Date')["Gross"].sum().reset_index()
new_sales_pc = round(
    ((daily_sales.iloc[-1]['Gross'] - daily_sales.iloc[-2]['Gross']) / daily_sales.iloc[-1]['Gross']) * 100, 2)

# day's best-selling item
day_best_seller = df.groupby(["Date", "Variants.Name"])['Variants.Quantity'].sum().reset_index().rename(
    columns={0: 'count'})
last_day = day_best_seller.iloc[-1]['Date']
day_best_seller = day_best_seller.loc[(day_best_seller['Date'] == last_day)]
day_best_seller.sort_values(by="Variants.Quantity", ascending=False, inplace=True)

# number of units sold
pr_unit = df['Variants.Quantity'].sum()

# units sold today
units_sold = df.groupby(["Date"])["Variants.Quantity"].sum().reset_index()
units_sold_today = units_sold.iloc[-1]['Variants.Quantity']

# items that have run out of stock and need to be refilled
out_of_stock = inv_df.loc[(inv_df['Data.Inventory'] < 0)]
oos = out_of_stock['Data.Inventory'].count()

# last time an item was purchased
last_date_sold = df.groupby(['Variants.Name'])["Date"].max().reset_index()
last_date_sold.sort_values(by="Date", ascending=False, inplace=True)

# time operations on data set
keys = [pair for pair, df in df.groupby(['hour'])]

app.css.append_css({
    "external_url": external_stylesheets
})


'''final app layout render'''
app.layout = html.Div(
    html.Div([
        # header row
        html.Div([
            html.Div([
                html.H3(children='Your latest insights'),
            ],
                className="one-half column", id="title"
            ),

            html.Div([
                html.H6(children='Last updated at ' + str(
                    df['Created'].iloc[-1].strftime("%B %d, %H:%M, %Y")) + ' +03:00 (GMT)',
                        style={'color': 'orange'}),
            ],
                className="one-third column", id="title"
            ),

        ], id='header', className='row flex-display', style={'margin-bottom': "25px"}),

        # first row
        html.Div([
            html.H6(
                children="Total Revenue",
                style={
                    'textAlign': 'center',
                    'color': 'black'
                }
            ),
            html.P(
                f"{df['Gross'].sum()}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 40
                }
            ),
            html.P(
                'new: ' + f"{daily_sales.iloc[-1]['Gross'] - daily_sales.iloc[-2]['Gross']}" + " (" + f"{new_sales_pc}" + '%)',
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontsize': 15,
                    'margin-top': '-10px'
                }
            )
        ],
            className="card_container three columns"
        ),

        html.Div([
            html.H6(
                children="Today's best seller",
                style={
                    'textAlign': 'center',
                    'color': 'black'
                }
            ),
            html.P(
                f"{day_best_seller.iloc[0]['Variants.Name']}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 40
                }
            ),
            html.P(
                'Units sold today: ' + f"{day_best_seller.iloc[0]['Variants.Quantity']}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontsize': 15,
                    'margin-top': '-10px'
                }
            )
        ],
            className="card_container three columns"
        ),

        html.Div([
            html.H6(
                children="Total units sold",
                style={
                    'textAlign': 'center',
                    'color': 'black'
                }
            ),
            html.P(
                f"{pr_unit}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 40
                }
            ),
            html.P(
                'Units sold today: ' + f"{units_sold_today}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontsize': 15,
                    'margin-top': '-10px'
                }
            )
        ],
            className="card_container three columns"
        ),

        html.Div([
            html.H6(
                children="Out of stock items",
                style={
                    'textAlign': 'center',
                    'color': 'black'
                }
            ),
            html.P(
                f"{oos}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 40
                }
            ),
            html.P(
                'Last updated: ' + f"{date.today().strftime('%Y/%m/%d')}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontsize': 15,
                    'margin-top': '-10px'
                }
            )
        ],
            className="card_container three columns"
        ),

        # Second Row
        html.Div([
            html.P(
                "Select Product: ",
                className='fix_label',
                style={
                    'color': 'white'
                }
            ),
            dcc.Dropdown(id="products",
                         multi=False,
                         clearable=True,
                         value="product",
                         placeholder="Select product...",
                         options=[{
                             'label': c,
                             'value': c
                         }
                             for c in (df['Variants.Name'].unique())], className="dcc_compon"),
            html.P(
                "Date last purchased: " + f"{date.today()}",
                className="fix_label",
                style={
                    'color': 'white',
                    'text-align': 'center'
                }
            ),
            dcc.Graph(id='quantity',
                      config={
                          'displayModeBar': False
                      },
                      className='dcc_compon',
                      style={
                          'margin-top': '20px'
                      }),

        ], className='create_container three columns', id='cross-filter-options'),
        html.Div([
            dcc.Graph(id='bar_chart',
                      config={
                          'displayModeBar': 'hover'
                      }),
        ], className='create_container three columns'),
        html.Div([
            dcc.Graph(id="line_chart")
        ], className='create_container six columns'),
    ], className='row flex-display'),
)


@app.callback(
    Output('quantity', 'figure'),
    [Input('products', 'value')]
)
def update_product(product):
    """day that a product was last sold"""
    per_item_quantity = df.groupby(['Date', 'Variants.Name'])['Variants.Quantity'].size().reset_index()
    last_sold_qty = per_item_quantity[per_item_quantity['Variants.Name'] == product].iloc[-1]['Variants.Quantity']

    delta_qty = per_item_quantity[per_item_quantity['Variants.Name'] == product].iloc[-1]['Variants.Quantity'] - \
                per_item_quantity[per_item_quantity['Variants.Name'] == product].iloc[-2]['Variants.Quantity']

    return {
        'data': [go.Indicator(
            mode='number+delta',
            value=last_sold_qty,
            delta={
                'reference': delta_qty,
                'position': 'right',
                'valueformat': ',g',
                'relative': False,
                'font': {
                    'size': 15
                }
            },
            number={
                'valueformat': ',',
                'font': {
                    'size': 20
                },
            },
            domain={
                'y': [0, 1],
                'x': [0, 1]
            }
        )],
        'layout': go.Layout(
            title={
                'text': 'Quantity sold today',
                'y': 1,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            font=dict(color='orange'),
            paper_bgcolor='slateblue',
            plot_bgcolor='slateblue',
            height=50
        ),
    }


@app.callback(
    Output("bar_chart", "figure"),
    [Input("products", "value")])
def generate_chart(products):
    product_daily_sales = df.groupby(['Date', 'Variants.Name'])['Variants.Quantity'].size().reset_index()

    return {
        'data': [
            go.Bar(x=product_daily_sales[product_daily_sales['Variants.Name'] == products]['Date'].tail(30),
                   y=product_daily_sales[product_daily_sales['Variants.Name'] == products]['Variants.Quantity'].tail(30),
                   name=f"Daily sales for {products}",
                   marker=dict(
                       color='orange'
                   ),
                   hoverinfo='text',
                   hovertext=
                   '<b>Date</b>: ' + product_daily_sales[product_daily_sales['Variants.Name'] == products]['Date'].tail(30).astype(str) + '<br>' +
                   '<b>Quantity Sold</b>: ' + product_daily_sales[product_daily_sales['Variants.Name'] == products]['Variants.Quantity'].tail(30).astype(str) + '<br>' +
                   '<b>Product</b>: ' + product_daily_sales[product_daily_sales['Variants.Name'] == products]['Variants.Name'].tail(30).astype(str) + '<br> '
                   )
        ],
        'layout': go.Layout(
            barmode='stack',
            plot_bgcolor='slateblue',
            paper_bgcolor='slateblue',
            title={
                'text': 'Quantity sold last 30 days for: ' + products,
                'y': 0.93,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            titlefont={
                'color': 'white',
                'size': 20
            },
            hovermode='x',
            xaxis=dict(
                title='<b>Date</b>',
                color='white',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='white',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='white'
                )
            ),
            yaxis=dict(
                title='<b>Quantity Sold</b>',
                color='white',
                showline=True,
                showgrid=True,
                showticklabels=True,
                linecolor='white',
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family='Arial',
                    size=12,
                    color='white'
                )
            ),
            legend={
                'orientation': 'h',
                'bgcolor': 'slategrey',
                'xanchor': 'center', 'x': 0.5, 'y': -0.3
            },
            font=dict(
                family='sans-serif',
                size=12,
                color='white'
            )
        )
    }


if __name__ == '__main__':
    app.run_server(debug=False)
