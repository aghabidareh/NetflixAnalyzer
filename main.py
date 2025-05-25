import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("netflix_titles.csv")
df['date_added'] = pd.to_datetime(df['date_added'])
df['release_year'] = df['release_year'].fillna(0).astype(int)
df['country'] = df['country'].fillna("Unknown")
df['listed_in'] = df['listed_in'].fillna("Unknown")

years = sorted(df['release_year'].unique())
countries = sorted(set(', '.join(df['country'].dropna()).split(', ')))
types = df['type'].unique()

app = dash.Dash(__name__)
app.title = "Netflix Dashboard"

app.layout = html.Div(style={
    'backgroundColor': '#121212',
    'color': 'white',
    'fontFamily': 'Arial, sans-serif',
    'padding': '20px'
}, children=[
    html.H1("🎬 Netflix Interactive Dashboard", style={'textAlign': 'center', 'color': '#E50914'}),

    html.Div([
        html.Div([
            html.Label("Select Year:", style={'marginBottom': '5px'}),
            dcc.Dropdown(
                options=[{'label': str(y), 'value': y} for y in years if y > 2000],
                value=2020,
                id='year-selector',
                style={'backgroundColor': '#1e1e1e', 'color': 'black'}
            )
        ], style={'width': '30%', 'display': 'inline-block', 'marginRight': '20px'}),

        html.Div([
            html.Label("Select Type:", style={'marginBottom': '5px'}),
            dcc.Dropdown(
                options=[{'label': t, 'value': t} for t in types],
                value='Movie',
                id='type-selector',
                style={'backgroundColor': '#1e1e1e', 'color': 'black'}
            )
        ], style={'width': '30%', 'display': 'inline-block'}),

        html.Div([
            html.Label("Select Country:", style={'marginBottom': '5px'}),
            dcc.Dropdown(
                options=[{'label': c, 'value': c} for c in countries],
                value='United States',
                id='country-selector',
                style={'backgroundColor': '#1e1e1e', 'color': 'black'}
            )
        ], style={'width': '35%', 'display': 'inline-block', 'marginTop': '0px'}),
    ], style={'marginBottom': '30px'}),

    dcc.Graph(id='content-by-genre', style={'marginBottom': '40px'}),
    dcc.Graph(id='rating-distribution', style={'marginBottom': '40px'}),
    dcc.Graph(id='yearly-content-trend')
])


