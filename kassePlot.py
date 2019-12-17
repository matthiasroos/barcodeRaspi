#!/usr/bin/python3
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


app = dash.Dash()

purchases_df = pd.read_csv('purchase.txt', header=None)
purchases_df.columns = ['timestamp', 'user', 'code']
purchases_df['code'] = purchases_df['code'].astype(str)

products_df = pd.read_csv('produkt.txt', header=None)
products_df.columns = ['nr', 'code', 'desc', 'price']
products_df['code'] = products_df['code'].astype(str)

purchases_df = purchases_df.merge(products_df, on='code', how='left', sort=False)

print(purchases_df)

grouped_df = purchases_df.groupby('user').count()

print(grouped_df)

users = grouped_df.index.tolist()
print(users)

app.layout = html.Div(children=[
    html.H1(children='barcodeRaspi Interactive App'),

    html.Div(children='''
        Analyze your drinking behavior and the one of your colleagues
    '''),
    dcc.Dropdown(
        options=[
            {'label': i, 'value': i } for i in users
        ],
        value='MTL'
    ),


    dcc.Graph(
        id='sum-of-drinks',
        figure={
            'data': [
                {'x': grouped_df.index, 'y': grouped_df['code'], 'type': 'bar'},
            ],
            'layout': {
                'title': 'Number of drinks per User'
            }
        }
    ),

])

if __name__ == '__main__':
    app.run_server(debug=True)