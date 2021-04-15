from collections import Counter
from datetime import date
from itertools import combinations

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Input, Output
from django_plotly_dash import DjangoDash

bs_theme = "https://bootswatch.com/4/darkly/bootstrap.min.css"
external_stylesheets = [bs_theme]

app = DjangoDash('sales')

'''
import data
----------------------------------------------------
we are using data from sales stored in our database
----------------------------------------------------
'''
conn_str = 'sqlite:////Users/erickamau/Library/Mobile Documents/com~apple~CloudDocs/Work/projects/jamboml/identifier.sqlite'
# sales
df = pd.read_sql_table('eda', conn_str)
# inventory
inv_df = pd.read_sql_table('inventory_clean', conn_str)

'''
dataframe operations
----------------------------------------------------
basic operations from on our dataset to come up with
values for our insights.
----------------------------------------------------
'''
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
df['Date'] = pd.to_datetime(df['Date'])
df = df.set_index('Date')
df['hour'] = df.index.hour
df = df.reset_index()

app.css.append_css({
    "external_url": external_stylesheets
})

# sidebar
# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    # "background-color": "dark-orange",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

'''
APPLICATION COMPONENTS
-------------------------------------------------
code for various components for the dashboard
and their callback functions.
-------------------------------------------------
'''

'''simple search box'''
search = html.Div(
    [
        dbc.Input(
            id="input",
            type="text",
            placeholder="Search for ...", bs_size="sm", className="mb-3"
        ),
        dbc.FormText("Type something in the box above", style={'color': 'white'}),
        html.Br(),
        html.P(id="output"),
    ]
)

# @app.callback(
#     Output("output", "children"), [Input("input", "value")]
# )
# def search_result(value):
#     # code for search parameters
#
#     return value


sidebar = html.Div(
    [
        html.H2("Jambo", className="display-4"),
        html.Hr(),
        html.P(
            "Welcome. Here are your latest insights", className="lead"
        ),
        search,
        dbc.Nav(
            [
                dbc.NavLink("Sales", href="/django_plotly_dash/app/sales/", active="exact"),
                dbc.NavLink("Inventory & Suppliers", href="/django_plotly_dash/app/sales/inventory-suppliers",
                            active="exact"),
                dbc.NavLink("Customers", href="/django_plotly_dash/app/sales/customers", active="exact"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

# navbar
navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.H6(children='Last updated at ' +
                                             str(df['Created'].iloc[-1].strftime("%B %d, %H:%M, %Y")) + ' +03:00 (GMT)',
                                    style={
                                        'color': 'orange',
                                        'margin-left': '56rem'
                                    }),
                        ),
                    ],
                    align="right",
                    no_gutters=True,
                ),
                href="https://plot.ly",
            ),
        ]
    ),
    color="dark",
    dark=True,
    className="mb-5",
)

"""
INDICATORS
---------------------------------------------------------
Code for indicators. These show an increase or decrease 
in compared values e.g sales between yesterday and today.
---------------------------------------------------------
"""

"""
CARDS
------------------------------------------------
Code for the various cards with various insights
e.g revenue, inventory etc
------------------------------------------------
"""

# total revenue
revenue_card = [
    dbc.CardBody(
        [
            html.H4("Total Revenue", className="card-title", style={'textAlign': 'center'}),
            html.P(
                f"{df['Gross'].sum()}",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 40
                }
            ),
            html.H6('new: ' + f"{daily_sales.iloc[-1]['Gross'] - daily_sales.iloc[-2]['Gross']}" + " (" +
                    f"{new_sales_pc}" + '%)', style={'textAlign': 'center'}),
            dbc.CardLink("See more", href="#"),
        ]
    ),
]

# total units sold
units_sold_card = [
    dbc.CardBody(
        [
            html.H4("Units sold", className="card-title", style={'textAlign': 'center'}),
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
            ),
            dbc.CardLink("See more", href="#"),
        ]
    ),
]

# day's best seller
best_seller_card = [
    dbc.CardBody(
        [
            html.H4(
                "Today's best seller",
                style={
                    'textAlign': 'center'
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
            ),
            dbc.CardLink("See more", href="#"),
        ]
    ),
]

# out of stock stuff
out_of_stock_card = [
    dbc.CardBody(
        [
            html.H4(
                children="Out of stock items",
                style={
                    'textAlign': 'center'
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
            ),
            dbc.CardLink("See more", href="#"),
        ]
    ),
]

# product dropdown
dropdown_card = [
    dbc.CardBody(
        [
            dcc.Dropdown(id="products",
                         multi=False,
                         clearable=True,
                         value="product",
                         placeholder="Select product...",
                         options=[{
                             'label': c,
                             'value': c
                         }
                             for c in (df['Variants.Name'].unique())], className="dcc_compon",
                         style={'color': 'black'}),
            html.P(
                "Date last purchased: " + f"{date.today()}",
                className="fix_label",
                style={
                    'color': 'white',
                    'text-align': 'center'
                }
            ),
        ]
    )
]

# last 30 days purchase graph
last_30_graph = [
    dbc.CardBody(
        [
            dcc.Graph(
                id='bar_chart',
                config={
                    'displayModeBar': 'hover'
                },
                style={
                    'height': 300,
                }
            ),
        ]
    )
]

# items sold together
sold_together = [
    dbc.CardBody(
        [
            html.H4(
                "This item goes well together with",
                style={
                    'textAlign': 'center'
                }
            ),
            html.Div(
                id="sold_with",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 40
                }
            ),
            html.P(
                "They have been sold together ",
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 15
                }
            ),
            html.Div(
                id="times",
                style={
                    'textAlign': 'center',
                    'color': 'orange',
                    'fontSize': 25
                }
            ),
            html.P(
                "times before.",
                style={
                    'textAlign': 'center',
                    'color': 'white',
                    'fontSize': 15
                }
            ),
        ]
    )
]

sold_times_graph = [
    dbc.CardBody(
        [
            html.H6(
                "Product selling times",
                style={
                    'textAlign': 'center'
                }
            ),
            dcc.Graph(
                id="item_sold_times_chart",
                config={
                    'displayModeBar': 'hover'
                },
                style={
                    'height': 300,
                }
            )
        ]
    )
]
'''putting the cards all together into a masonry kind of layout'''
card_row_1 = dbc.CardColumns(
    [
        dbc.Card(dropdown_card, body=True),
        dbc.Card(revenue_card, body=True),
        dbc.Card(last_30_graph, color='dark', inverse=True),
        dbc.Card(sold_together, body=True),
        dbc.Card(sold_times_graph, body=True),
        dbc.Card(units_sold_card, body=True),
        dbc.Card(best_seller_card, body=True),
        dbc.Card(out_of_stock_card, body=True)
    ]
)

content = html.Div(
    [
        dbc.Row(
            [
                card_row_1
            ]
        ),
    ],
    id="page-content", style=CONTENT_STYLE
)

'''final app layout render'''
app.layout = html.Div(
    [navbar, content, sidebar]
)


# @app.callback(
#     Output("page-content", "children"), [Input("url", "pathname")]
# )
# def render_page_content(pathname):
#     if pathname == "/django_plotly_dash/app/sales/":
#         return html.P("This is the content of the home page!")
#     elif pathname == "/django_plotly_dash/app/sales/page-1":
#         return html.P("This is the content of page 1. Yay!")
#     elif pathname == "/django_plotly_dash/app/sales/page-2":
#         return html.P("Oh cool, this is page 2!")
#
#     # If the user tries to reach a different page, return a 404 message
#     return dbc.Jumbotron(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The pathname {pathname} was not recognised..."),
#         ]
#     )

@app.callback(
    [Output("sold_with", "children"),
     Output("times", "children")],
    [Input("products", "value")]
)
def get_item_sold_together(products):
    # operation to find items that are sold together
    df_dup = df[df['Number'].duplicated(keep=False)]
    df_dup['Items.Grouped'] = df_dup.groupby('Number')['Variants.Name'].transform(lambda x: ', '.join(x))
    df_dup = df_dup[['Number', 'Items.Grouped']].drop_duplicates()

    count = Counter()

    for row in df_dup['Items.Grouped']:
        row_list = row.split(',')
        count.update(Counter(combinations(row_list, 2)))

    grp_count = count.most_common()

    df_grp = pd.DataFrame(grp_count)
    df_grp.columns = ['combination', 'count']
    df_grp = df_grp[(df_grp['count'] >= 5)]
    df_grp.reset_index()
    combs = pd.DataFrame(df_grp.combination.values.tolist(), index=df_grp.index, columns=['Comb1', 'Comb2'])
    df_grp = pd.concat([df_grp, combs], axis=1, join='inner', ignore_index=False)
    df_grp.sort_values(by='count', ascending=False, inplace=True)

    try:
        comb_item, comb_count = df_grp[df_grp["Comb1"] == products].reset_index().iloc[0][['Comb2', 'count']]
        return comb_item, comb_count
    except IndexError:
        return dash.no_update, "There is no ideal combinator for this item at this time"


@app.callback(
    Output("item_sold_times_chart", "figure"),
    [Input("products", "value")]
)
def generate_sold_times_chart(products):
    product_df = df[(df['Variants.Name'] == products)]
    product_df = product_df.groupby(['hour']).size().reset_index(name="counts")

    fig = px.line(product_df, x='hour', y='counts')

    return fig


@app.callback(
    Output("bar_chart", "figure"),
    [Input("products", "value")])
def generate_chart(products):
    product_daily_sales = df.groupby(['Date', 'Variants.Name'])['Variants.Quantity'].size().reset_index()

    return {
        'data': [
            go.Bar(x=product_daily_sales[product_daily_sales['Variants.Name'] == products]['Date'].tail(30),
                   y=product_daily_sales[product_daily_sales['Variants.Name'] == products]['Variants.Quantity'].tail(
                       30),
                   name=f"Daily sales for {products}",
                   marker=dict(
                       color='orange'
                   ),
                   hoverinfo='text',
                   hovertext=
                   '<b>Date</b>: ' + product_daily_sales[product_daily_sales['Variants.Name'] == products]['Date'].tail(
                       30).astype(str) + '<br>' +
                   '<b>Quantity Sold</b>: ' + product_daily_sales[product_daily_sales['Variants.Name'] == products][
                       'Variants.Quantity'].tail(30).astype(str) + '<br>' +
                   '<b>Product</b>: ' + product_daily_sales[product_daily_sales['Variants.Name'] == products][
                       'Variants.Name'].tail(30).astype(str) + '<br> '
                   )
        ],
        'layout': go.Layout(
            barmode='stack',
            plot_bgcolor='slategrey',
            paper_bgcolor='slategrey',
            title={
                'text': 'Last 30 days for: ' + products,
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
