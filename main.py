import pandas as pd
import plotly.express as px
from dash import Dash, html, dcc, Input, Output
import dash_bootstrap_components as dbc

# Load Data
df = pd.read_csv('netflix_titles.csv')
