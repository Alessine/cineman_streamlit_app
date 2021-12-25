import streamlit as st
import pandas as pd
from datetime import date
import visualization.plotting_functions as pf
import models.reco_functions as rf


def create_app(cineman_df, movie_desc, all_movies_desc, similarities_df, MAPBOX_ACCESS_TOKEN):
    # Header
    st.title(f"Movies in Zurich, {date.today()}")

    # First all the stuff that goes in the sidebar
    st.sidebar.header("Get a Movie Recommendation")
    all_movies = ["None"] + sorted(pd.unique(all_movies_desc['original_title']))
    favorite_movie = st.sidebar.selectbox("What is your favorite movie?", options=all_movies)
    selected_movie = "All"

    if favorite_movie != "None":
        movie_rec = rf.recent_movie_recommender(movie_title=favorite_movie, all_movies_desc=all_movies_desc,
                                                recent_movies_desc=movie_desc, similarities_df=similarities_df)
        st.sidebar.write(f"<b>Recommended Movie:</b><br>{movie_rec}", unsafe_allow_html=True)
        overview = pf.fetch_movie_desc(movie_desc, movie_rec)
        st.sidebar.markdown(f'{overview}', unsafe_allow_html=True)
        selected_movie = movie_rec

    st.sidebar.header("Choose What to Watch")
    # Select the timeframe
    hours = ["All", "9-12am", "12-3pm", "3-6pm", "6-9pm", "9-12pm"]
    selected_hour = st.sidebar.select_slider("Show movies that start between:", options=hours)
    cineman_df_hour = pf.select_by_hour(cineman_df, hour=selected_hour)

    # Select a specific movie
    recent_movies = ["All"]+sorted(pd.unique(cineman_df_hour['movie']))
    movie_choice = st.sidebar.selectbox("Choose a Movie", options=recent_movies)

    # Add the movie description
    overview = pf.fetch_movie_desc(movie_desc, movie_choice)
    st.sidebar.markdown(f'{overview}', unsafe_allow_html=True)
    if movie_choice != "All":
        selected_movie = movie_choice

    # Set up the main page
    left, right = st.columns([2, 1])

    # Create the map
    plotly_map = pf.create_plotly_map(df=cineman_df_hour, MAPBOX_ACCESS_TOKEN=MAPBOX_ACCESS_TOKEN,
                                      hour=selected_hour, movie=selected_movie)
    left.plotly_chart(plotly_map)

    # Credits for the data
    st.write("Data scraped from www.cineman.ch")
