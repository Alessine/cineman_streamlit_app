#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd
from datetime import date

import data.cineman_scraping as cs
from data.tmdb_api import get_specific_movie_overviews
from visualization.cineman_streamlit_app import create_app


def main():
    # Reading in user-dependent variables: file paths
    data_path_shows = eval(os.getenv("DATA_PATH_SHOWS"))
    data_path_desc = eval(os.getenv("DATA_PATH_DESC"))
    mapbox_access_path = os.getenv("MAPBOX_ACCESS_PATH")

    # Try loading saved data
    try:
        cineman_df = pd.read_csv(data_path_shows)
        movie_desc = pd.read_csv(data_path_desc)

    # If files don't exist yet, go ahead and scrape the data
    except FileNotFoundError:
        # Reading in user-dependent variables: credentials etc.
        google_credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        tmdb_ids_file_path = os.getenv("TMDB_IDS_FILE_PATH")
        tmdb_credentials_path = os.getenv("TMDB_CREDENTIALS_PATH")

        # Scraping the most recent data and saving it
        content = cs.scrape_cineman(cities=("Zürich"))
        movie_program_df = cs.format_cineman_content(html_content=content)
        cs.get_theatre_coordinates(showtimes_df=movie_program_df, GOOGLE_CREDENTIALS_PATH=google_credentials_path,
                                   DATA_PATH_SHOWS=data_path_shows)

        # Requesting movie overviews via the tmdb api and saving them
        get_specific_movie_overviews(TMDB_IDS_FILE_PATH=tmdb_ids_file_path, TMDB_CREDENTIALS_PATH=tmdb_credentials_path,
                                     DATA_PATH_SHOWS=data_path_shows, DATA_PATH_DESC=data_path_desc, movies_list=None)

        # Loading the saved data
        cineman_df = pd.read_csv(data_path_shows)
        movie_desc = pd.read_csv(data_path_desc)

    # Create the app
    create_app(cineman_df=cineman_df, movie_desc=movie_desc, MAPBOX_ACCESS_PATH=mapbox_access_path)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
