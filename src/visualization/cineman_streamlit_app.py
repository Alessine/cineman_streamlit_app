import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date

import plotting_functions as pf

# Read in the data
cineman_df = pd.read_csv(f"../../data/raw/{date.today()}_showtimes.csv", index_col=0)
mapbox_access_token = open("../../.mapbox_token").read()
movie_desc = pd.read_csv(f"../../data/raw/{date.today()}_zurich_movie_overviews.csv")

# Cleaning (added to scraping script)
cineman_df["dt_showtime"] = cineman_df["date"] + " " + cineman_df["showtime"]
cineman_df["dt_showtime"] = pd.to_datetime(cineman_df["dt_showtime"], format= '%Y-%m-%d %H:%M')

# Headers
st.title(f"Movies in Zurich, {date.today()}")
st.sidebar.header("Options for Selection")
#st.sidebar.subheader("Options for Selection")

# Set up of the page
left, right = st.columns([2, 1])

# Select the timeframe
hours = ["All", "9-12am", "12-3pm", "3-6pm", "6-9pm", "9-12pm"]
selected_hour = st.sidebar.select_slider("Show movies that start between:", options=hours)
cineman_df_hour = pf.select_by_hour(cineman_df, hour=selected_hour)

# Select a specific movie
movies = ["All"]+sorted(pd.unique(cineman_df_hour['movie']))
selected_movie = st.sidebar.selectbox("Choose a Movie", options=movies)   # Here the selection of the year.

# Add the movie description
overview = pf.fetch_movie_desc(movie_desc, selected_movie)
st.sidebar.markdown(f'{overview}', unsafe_allow_html=True)

# Create the map
plotly_map = pf.create_plotly_map(cineman_df_hour, mapbox_access_token, hour=selected_hour, movie=selected_movie)
left.plotly_chart(plotly_map)

# Credits for the data
st.write("Data scraped from www.cineman.ch")
