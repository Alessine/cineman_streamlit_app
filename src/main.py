#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd
from datetime import date
from visualization.cineman_streamlit_app import create_app


def main():
    data_path_shows = eval(os.getenv("DATA_PATH_SHOWS"))
    cineman_df = pd.read_csv(data_path_shows)

    mapbox_access_path = os.getenv("MAPBOX_ACCESS_PATH")
    mapbox_access_token = open(mapbox_access_path).read()

    data_path_desc = eval(os.getenv("DATA_PATH_DESC"))
    movie_desc = pd.read_csv(data_path_desc)

    create_app(cineman_df, movie_desc, mapbox_access_token)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
