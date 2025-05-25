import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Load Data
df = pd.read_csv('netflix_titles.csv')

# Data Preprocessing
df['date_added'] = pd.to_datetime(df['date_added'], errors='coerce')
df['year_added'] = df['date_added'].dt.year
df['month_added'] = df['date_added'].dt.to_period('M')
df['release_year'] = pd.to_numeric(df['release_year'], errors='coerce')
df['country_clean'] = df['country'].dropna().str.split(',').str[0].str.strip()

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

app.layout = dbc.Container([
    html.H1("🎬 Netflix Dashboard", className="text-center my-4"),

    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='content_type',
                options=[{'label': i, 'value': i} for i in df['type'].dropna().unique()],
                value='Movie',
                clearable=False
            ),
            dcc.Graph(id='release_trend')
        ], width=6),

        dbc.Col([
            dcc.Graph(
                id='country_dist',
                figure=px.bar(df['country_clean'].value_counts().nlargest(10).reset_index(),
                              x='index', y='country_clean',
                              labels={'index': 'Country', 'country_clean': 'Count'},
                              title='Top 10 Countries by Content')
            )
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='genre_bar',
                figure=px.bar(
                    pd.Series([g.strip() for sublist in df['listed_in'].dropna().str.split(',') for g in sublist])
                    .value_counts().nlargest(10).reset_index(),
                    x='index', y=0,
                    labels={'index': 'Genre', 0: 'Count'},
                    title='Top Genres on Netflix'
                )
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                id='rating_dist',
                figure=px.pie(
                    df['rating'].dropna().value_counts().nlargest(6).reset_index(),
                    names='index', values='rating',
                    title='Content Rating Distribution'
                )
            )
        ], width=6)
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='monthly_additions',
                figure=px.line(
                    df.groupby('month_added').size().reset_index(name='count'),
                    x='month_added', y='count',
                    title='Monthly Content Additions Over Time'
                )
            )
        ])
    ])
], fluid=True)

@app.callback(
    Output('release_trend', 'figure'),
    Input('content_type', 'value')
)
def update_release_trend(selected_type):
    filtered_df = df[df['type'] == selected_type]
    trend = filtered_df['release_year'].value_counts().sort_index()
    fig = px.line(x=trend.index, y=trend.values, labels={'x': 'Release Year', 'y': 'Number of Titles'},
                  title=f'{selected_type} Releases Over the Years')
    return fig

