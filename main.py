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
