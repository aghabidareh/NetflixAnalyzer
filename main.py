import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv("netflix_titles.csv")
df['date_added'] = pd.to_datetime(df['date_added'].str.strip(), errors='coerce')
df['release_year'] = df['release_year'].fillna(0).astype(int)
df['country'] = df['country'].fillna("Unknown")
df['listed_in'] = df['listed_in'].fillna("Unknown")
df['cast'] = df['cast'].fillna("Unknown")
df['duration'] = df['duration'].fillna("Unknown")

all_casts = df['cast'].str.split(', ').explode().value_counts().nlargest(50).index.tolist()

df['duration_int'] = df['duration'].str.extract('(\d+)').astype(float)
df['duration_type'] = df['duration'].str.extract('([a-zA-Z]+)')
df['duration_int'] = df['duration_int'].fillna(0)

app = dash.Dash(__name__)
app.title = "Netflix Dashboard V2"

app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("🎬 Netflix Dashboard – Advanced Filters", style={'textAlign': 'center', 'color': '#E50914'}),

    html.Div([
        html.Div([
            html.Label("Select Year Range:"),
            dcc.RangeSlider(
                min=2000, max=2021, step=1,
                marks={y: str(y) for y in range(2000, 2022, 2)},
                value=[2015, 2020],
                id='year-range'
            )
        ], style={'width': '100%', 'marginBottom': '25px'}),

        html.Div([
            html.Label("Select Type:"),
            dcc.Dropdown(
                options=[{'label': t, 'value': t} for t in df['type'].unique()],
                value='Movie',
                id='type-selector'
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                options=[{'label': c, 'value': c} for c in sorted(set(', '.join(df['country']).split(', ')))],
                value='United States',
                id='country-selector'
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            html.Label("Select Actor:"),
            dcc.Dropdown(
                options=[{'label': actor, 'value': actor} for actor in all_casts],
                value='Robert De Niro',
                id='actor-selector'
            )
        ], style={'width': '32%', 'display': 'inline-block'}),
    ]),

    html.Div([
        html.Label("Select Movie Duration Range (Minutes):"),
        dcc.RangeSlider(
            min=0, max=200, step=10,
            marks={i: str(i) for i in range(0, 201, 30)},
            value=[60, 120],
            id='duration-slider'
        )
    ], style={'marginTop': '30px', 'marginBottom': '40px'}),

    dcc.Graph(id='genre-bar'),
    dcc.Graph(id='rating-pie'),
    dcc.Graph(id='year-trend')
])

@app.callback(
    [Output('genre-bar', 'figure'),
     Output('rating-pie', 'figure'),
     Output('year-trend', 'figure')],
    [Input('year-range', 'value'),
     Input('type-selector', 'value'),
     Input('country-selector', 'value'),
     Input('actor-selector', 'value'),
     Input('duration-slider', 'value')]
)
def update_dashboard(year_range, type_selected, country_selected, actor_selected, duration_range):
    filtered = df[
        (df['release_year'] >= year_range[0]) &
        (df['release_year'] <= year_range[1]) &
        (df['type'] == type_selected) &
        (df['country'].str.contains(country_selected)) &
        (df['cast'].str.contains(actor_selected)) &
        ((df['duration_int'] >= duration_range[0]) & (df['duration_int'] <= duration_range[1]) if type_selected == 'Movie' else True)
    ]

    genre = filtered['listed_in'].str.split(',').explode().str.strip().value_counts().nlargest(10)
    fig_genre = px.bar(
        x=genre.index, y=genre.values,
        labels={'x': 'Genre', 'y': 'Count'},
        title='Top Genres',
        color_discrete_sequence=['#E50914']
    )
    fig_genre.update_layout(template='plotly_dark')

    rating = filtered['rating'].value_counts().nlargest(10)
    fig_rating = px.pie(
        names=rating.index, values=rating.values,
        title='Rating Distribution',
        color_discrete_sequence=px.colors.sequential.Reds
    )
    fig_rating.update_layout(template='plotly_dark')

    trend = df[(df['type'] == type_selected)].groupby('release_year').size()
    fig_trend = px.line(
        x=trend.index, y=trend.values,
        labels={'x': 'Year', 'y': 'Number of Titles'},
        title='Content Trend Over Years',
        markers=True,
        color_discrete_sequence=['#08F7FE']
    )
    fig_trend.update_layout(template='plotly_dark')

    return fig_genre, fig_rating, fig_trend

