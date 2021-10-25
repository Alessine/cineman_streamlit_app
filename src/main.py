#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd
from datetime import date

import data.cineman_scraping as cs
from visualization.cineman_streamlit_app import create_app


def main():
    # Reading in the user-dependent variables
    data_path_shows = eval(os.getenv("DATA_PATH_SHOWS"))
    google_credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")

    mapbox_access_path = os.getenv("MAPBOX_ACCESS_PATH")
    mapbox_access_token = open(mapbox_access_path).read()

    data_path_desc = eval(os.getenv("DATA_PATH_DESC"))

    #Scraping the most recent data and saving it
    content = cs.scrape_cineman(cities=("Zürich"))
    movie_program_df = cs.format_cineman_content(content)
    cs.get_theatre_coordinates(movie_program_df, google_credentials_path, data_path_shows)

    # Loading the saved data
    cineman_df = pd.read_csv(data_path_shows)
    movie_desc = pd.read_csv(data_path_desc)

    # Create the app
    create_app(cineman_df, movie_desc, mapbox_access_token)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
