import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

# Read in the data
cineman_df = pd.read_csv(f"../../data/raw/{date.today()}_showtimes.csv", index_col=0)
mapbox_access_token = open("../../.mapbox_token").read()


# Plotting functions
def create_plotly_map(df, access_token):
    fig = go.Figure(go.Scattermapbox(
        lat=df["latitude"],
        lon=df["longitude"],
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=10, color="crimson"
        ),
        text=df["cinema"],
        hoverinfo="text"
    ))

    fig.update_layout(
        hovermode='closest',
        width=500,
        height=500,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        mapbox=dict(
            accesstoken=access_token,
            center=go.layout.mapbox.Center(
                lat=47.374,
                lon=8.535
            ),
            zoom=12.5,
            style="streets"
        )
    )
    return fig


# Header and text
st.title(f"Movies in Zurich, {date.today()}")

# st.sidebar.header("Options for Selection")

# Set up of the page
st.sidebar.subheader("Options for Selection")
left, right = st.columns([2, 1])

# Widgets
# selectBox

movies = ["All"]+sorted(pd.unique(cineman_df['movie']))
movies = st.sidebar.selectbox("Choose a Movie", movies)   # Here the selection of the year.

# Create the map
plotly_map = create_plotly_map(cineman_df, mapbox_access_token)
left.plotly_chart(plotly_map)

# Credits for the data
st.write("Data scraped from www.cineman.ch")

