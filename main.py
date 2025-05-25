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

@app.callback(
    [Output('content-by-genre', 'figure'),
     Output('rating-distribution', 'figure'),
     Output('yearly-content-trend', 'figure')],
    [Input('year-selector', 'value'),
     Input('type-selector', 'value'),
     Input('country-selector', 'value')]
)
def update_graphs(selected_year, selected_type, selected_country):
    filtered_df = df[(df['release_year'] == selected_year) &
                     (df['type'] == selected_type) &
                     (df['country'].str.contains(selected_country))]

    genre_split = filtered_df['listed_in'].str.split(',').explode().str.strip()
    genre_counts = genre_split.value_counts().nlargest(10)
    fig_genre = px.bar(
        x=genre_counts.index, y=genre_counts.values,
        labels={'x': 'Genre', 'y': 'Count'},
        title=f"Top Genres ({selected_year})",
        color_discrete_sequence=['#E50914']
    )
    fig_genre.update_layout(template='plotly_dark')

    rating_counts = filtered_df['rating'].value_counts().nlargest(10)
    fig_rating = px.pie(
        names=rating_counts.index, values=rating_counts.values,
        title='Rating Distribution',
        color_discrete_sequence=px.colors.sequential.Reds
    )
    fig_rating.update_layout(template='plotly_dark')

    year_count = df[df['type'] == selected_type].groupby('release_year').size()
    fig_trend = px.line(
        x=year_count.index, y=year_count.values,
        labels={'x': 'Year', 'y': 'Number of Titles'},
        title='Titles Over the Years',
        markers=True,
        color_discrete_sequence=['#08F7FE']
    )
    fig_trend.update_layout(template='plotly_dark')

    return fig_genre, fig_rating, fig_trend

if __name__ == '__main__':
    app.run_server(debug=True)
