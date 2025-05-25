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
