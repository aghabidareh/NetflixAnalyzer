import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px
import re

# Load and preprocess data
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
    fig = px.scatter(x=[0], y=[0], labels={'x': '', 'y': ''}, title=f"{title}")
    fig.update_traces(marker=dict(size=0))
    fig.update_layout(
        template='plotly_dark',
        showlegend=False,
        annotations=[{
            'text': 'No Data Available for Selected Filters',
            'xref': 'paper',
            'yref': 'paper',
            'x': 0.5,
            'y': 0.5,
            'showarrow': False,
            'font': {'size': 20, 'color': '#E50914'}
        }]
    )
    return fig


app = dash.Dash(__name__, external_stylesheets=[
    'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
])
app.title = "Netflix Dashboard V2"

app.layout = html.Div(
    style={
        'background': 'linear-gradient(135deg, #141414 0%, #1c2526 100%)',
        'color': 'white',
        'padding': '40px',
        'fontFamily': 'Roboto, sans-serif',
        'minHeight': '100vh'
    },
    children=[
        html.Div(
            html.H1(
                children=[html.I(className='fas fa-film', style={'marginRight': '10px'}),
                          "Netflix Analytics Dashboard"],
                style={
                    'textAlign': 'center',
                    'color': '#E50914',
                    'fontSize': '36px',
                    'fontWeight': '700',
                    'marginBottom': '30px'
                }
            )
        ),

        html.Div(
            children=[
                html.H3("Filter Options", style={'color': '#E50914', 'marginBottom': '20px'}),
                html.Div([
                    html.Label("Select Year Range:", style={'fontSize': '16px', 'marginBottom': '10px'}),
                    dcc.RangeSlider(
                        min=min_year, max=max_year, step=1,
                        marks={y: str(y) for y in range(min_year, max_year + 1, 2)},
                        value=[max(min_year, 2015), min(max_year, 2020)],
                        id='year-range',
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    )
                ], style={'marginBottom': '30px'}),

                html.Div([
                    html.Div([
                        html.Label("Select Type:", style={'fontSize': '16px'}),
                        dcc.Dropdown(
                            options=[{'label': t, 'value': t} for t in df['type'].unique() if pd.notna(t)],
                            value='Movie',
                            id='type-selector',
                            style={'backgroundColor': '#2a2a2a', 'color': 'white', 'border': 'none'}
                        )
                    ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

                    html.Div([
                        html.Label("Select Country:", style={'fontSize': '16px'}),
                        dcc.Dropdown(
                            options=[{'label': c, 'value': c} for c in all_countries],
                            value='United States' if 'United States' in all_countries else all_countries[
                                0] if all_countries else 'Unknown',
                            id='country-selector',
                            style={'backgroundColor': '#2a2a2a', 'color': 'white', 'border': 'none'}
                        )
                    ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),

                    html.Div([
                        html.Label("Select Actor:", style={'fontSize': '16px'}),
                        dcc.Dropdown(
                            options=[{'label': actor, 'value': actor} for actor in all_casts],
                            value='Robert De Niro' if 'Robert De Niro' in all_casts else all_casts[
                                0] if all_casts else 'Unknown',
                            id='actor-selector',
                            style={'backgroundColor': '#2a2a2a', 'color': 'white', 'border': 'none'}
                        )
                    ], style={'width': '32%', 'display': 'inline-block'}),
                ], style={'display': 'flex', 'justifyContent': 'space-between'}),

                html.Div([
                    html.Label("Select Movie Duration (Minutes):", style={'fontSize': '16px', 'marginTop': '20px'}),
                    dcc.RangeSlider(
                        min=0, max=200, step=10,
                        marks={i: str(i) for i in range(0, 201, 30)},
                        value=[60, 120],
                        id='duration-slider',
                        tooltip={'placement': 'bottom', 'always_visible': True}
                    )
                ], style={'marginTop': '20px'}),
            ],
            style={
                'backgroundColor': '#1f1f1f',
                'padding': '20px',
                'borderRadius': '10px',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.3)',
                'marginBottom': '40px'
            }
        ),

        dcc.Loading(
            id="loading",
            type="circle",
            children=[
                html.Div([
                    dcc.Graph(id='genre-bar', style={'height': '400px'}),
                    dcc.Graph(id='rating-pie', style={'height': '400px'}),
                    dcc.Graph(id='year-trend', style={'height': '400px'}),
                ], style={
                    'display': 'grid',
                    'gridTemplateColumns': '1fr 1fr',
                    'gap': '20px'
                })
            ]
        )
    ]
)


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
        return create_empty_figure("Top Genres"), create_empty_figure("Rating Distribution"), create_empty_figure(
            "Content Trend Over Years")

    filtered = df[
        (df['release_year'] >= year_range[0]) &
        (df['release_year'] <= year_range[1]) &
        (df['type'] == type_selected)
        ]

    if country_selected:
        filtered = filtered[filtered['country'].str.contains(re.escape(country_selected), case=scrape_text, na=False)]
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
        return create_empty_figure("Top Genres"), create_empty_figure("Rating Distribution"), create_empty_figure(
            "Content Trend Over Years")

    genre = filtered['listed_in'].str.split(',').explode().str.strip().value_counts().nlargest(10)
    fig_genre = px.bar(
        x=genre.index, y=genre.values,
        labels={'x': 'Genre', 'y': 'Count'},
        title='Top Genres',
        color_discrete_sequence=['#E50914']
    ) if not genre.empty else create_empty_figure("Top Genres")
    fig_genre.update_layout(
        template='plotly_dark',
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        xaxis={'tickangle': 45},
        font={'family': 'Roboto', 'size': 14}
    )
    fig_genre.update_traces(hovertemplate='%{x}: %{y} titles')

    rating = filtered['rating'].value_counts().nlargest(10)
    fig_rating = px.pie(
        names=rating.index, values=rating.values,
        title='Rating Distribution',
        color_discrete_sequence=px.colors.sequential.Reds
    ) if not rating.empty else create_empty_figure("Rating Distribution")
    fig_rating.update_layout(
        template='plotly_dark',
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        font={'family': 'Roboto', 'size': 14}
    )
    fig_rating.update_traces(textinfo='percent+label', hovertemplate='%{label}: %{value} titles (%{percent})')

    trend = filtered.groupby('release_year').size()
    fig_trend = px.line(
        x=trend.index, y=trend.values,
        labels={'x': 'Year', 'y': 'Number of Titles'},
        title='Content Trend Over Years',
        markers=True,
        color_discrete_sequence=['#08F7FE']
    ) if not trend.empty else create_empty_figure("Content Trend Over Years")
    fig_trend.update_layout(
        template='plotly_dark',
        title={'x': 0.5, 'xanchor': 'center', 'font': {'size': 20}},
        font={'family': 'Roboto', 'size': 14}
    )
    fig_trend.update_traces(hovertemplate='Year: %{x}<br>Titles: %{y}')

    return fig_genre, fig_rating, fig_trend


if __name__ == '__main__':
    app.run(debug=True)
