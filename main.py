import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import re

try:
    df = pd.read_csv("netflix_titles.csv")
except FileNotFoundError:
    print("Error: 'netflix_titles.csv' not found. Please ensure the file is in the correct directory.")
    exit()

df['date_added'] = pd.to_datetime(df['date_added'].str.strip(), errors='coerce')
df['release_year'] = df['release_year'].fillna(0).astype(int)
df['country'] = df['country'].fillna("Unknown")
df['listed_in'] = df['listed_in'].fillna("Unknown")
df['cast'] = df['cast'].fillna("Unknown")
df['rating'] = df['rating'].fillna("Unknown")
df['duration'] = df['duration'].fillna("Unknown")

df['duration_int'] = df['duration'].str.extract(r'(\d+)').astype(float).fillna(0)
df['duration_type'] = df['duration'].str.extract('([a-zA-Z]+)').fillna("Unknown")

all_casts = df['cast'].str.split(', ').explode().str.strip().value_counts().nlargest(50).index.tolist()
all_countries = sorted(set(c for c in df['country'].str.split(', ').explode().str.strip() if c and c != "Unknown"))

min_year = max(2000, df[df['release_year'] > 0]['release_year'].min())
max_year = df['release_year'].max()

def create_empty_figure(title):
    fig = px.scatter(x=[0], y=[0], labels={'x': '', 'y': ''}, title=f"{title} (No Data Available)")
    fig.update_traces(marker=dict(size=0))  # Hide the scatter point
    fig.update_layout(template='plotly_dark', showlegend=False)
    return fig

app = dash.Dash(__name__)
app.title = "Netflix Dashboard V2"

app.layout = html.Div(style={'backgroundColor': '#121212', 'color': 'white', 'padding': '20px'}, children=[
    html.H1("🎬 Netflix Dashboard – Advanced Filters", style={'textAlign': 'center', 'color': '#E50914'}),

    html.Div([
        html.Div([
            html.Label("Select Year Range:"),
            dcc.RangeSlider(
                min=min_year, max=max_year, step=1,
                marks={y: str(y) for y in range(min_year, max_year + 1, 2)},
                value=[max(min_year, 2015), min(max_year, 2020)],
                id='year-range'
            )
        ], style={'width': '100%', 'marginBottom': '25px'}),

        html.Div([
            html.Label("Select Type:"),
            dcc.Dropdown(
                options=[{'label': t, 'value': t} for t in df['type'].unique() if pd.notna(t)],
                value='Movie',
                id='type-selector'
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            html.Label("Select Country:"),
            dcc.Dropdown(
                options=[{'label': c, 'value': c} for c in all_countries],
                value='United States' if 'United States' in all_countries else all_countries[0] if all_countries else 'Unknown',
                id='country-selector'
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

        html.Div([
            html.Label("Select Actor:"),
            dcc.Dropdown(
                options=[{'label': actor, 'value': actor} for actor in all_casts],
                value='Robert De Niro' if 'Robert De Niro' in all_casts else all_casts[0] if all_casts else 'Unknown',
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
    if not all([year_range, type_selected, country_selected, actor_selected, duration_range]):
        return create_empty_figure("Top Genres"), create_empty_figure("Rating Distribution"), create_empty_figure("Content Trend Over Years")

    filtered = df[
        (df['release_year'] >= year_range[0]) &
        (df['release_year'] <= year_range[1]) &
        (df['type'] == type_selected)
    ]

    if country_selected:
        filtered = filtered[filtered['country'].str.contains(re.escape(country_selected), case=False, na=False)]
    if actor_selected:
        filtered = filtered[filtered['cast'].str.contains(re.escape(actor_selected), case=False, na=False)]

    if type_selected == 'Movie':
        filtered = filtered[
            (filtered['duration_int'] >= duration_range[0]) &
            (filtered['duration_int'] <= duration_range[1]) &
            (filtered['duration_type'].str.contains('min', case=False, na=False))
        ]
    else:
        filtered = filtered[
            (filtered['duration_int'] > 0) &
            (filtered['duration_type'].str.contains('Season', case=False, na=False))
        ]

    if filtered.empty:
        return create_empty_figure("Top Genres"), create_empty_figure("Rating Distribution"), create_empty_figure("Content Trend Over Years")

    genre = filtered['listed_in'].str.split(',').explode().str.strip().value_counts().nlargest(10)
    fig_genre = px.bar(
        x=genre.index, y=genre.values,
        labels={'x': 'Genre', 'y': 'Count'},
        title='Top Genres',
        color_discrete_sequence=['#E50914']
    ) if not genre.empty else create_empty_figure("Top Genres")
    fig_genre.update_layout(template='plotly_dark')

    rating = filtered['rating'].value_counts().nlargest(10)
    fig_rating = px.pie(
        names=rating.index, values=rating.values,
        title='Rating Distribution',
        color_discrete_sequence=px.colors.sequential.Reds
    ) if not rating.empty else create_empty_figure("Rating Distribution")
    fig_rating.update_layout(template='plotly_dark')

    trend = filtered.groupby('release_year').size()
    fig_trend = px.line(
        x=trend.index, y=trend.values,
        labels={'x': 'Year', 'y': 'Number of Titles'},
        title='Content Trend Over Years',
        markers=True,
        color_discrete_sequence=['#08F7FE']
    ) if not trend.empty else create_empty_figure("Content Trend Over Years")
    fig_trend.update_layout(template='plotly_dark')

    return fig_genre, fig_rating, fig_trend

if __name__ == '__main__':
    app.run(debug=True)