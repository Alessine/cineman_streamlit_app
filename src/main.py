#!/usr/bin/env python
# coding: utf-8

import os
from dotenv import find_dotenv, load_dotenv
import pandas as pd
from datetime import date
import pickle

import data.cineman_scraping as cs
from data.tmdb_api import get_specific_movie_overviews
from visualization.cineman_streamlit_app import create_app
from features.corpus_prep import process_kaggle_tmdb_dataset, generate_movie_corpus
from models.reco_functions import train_ft_model


def main():
    # Reading in user-dependent variables: file paths
    data_path_shows = eval(os.getenv("DATA_PATH_SHOWS"))
    data_path_desc = eval(os.getenv("DATA_PATH_DESC"))


    # Try loading saved data on movies currently running in Zurich
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

    # If it's a Thursday, create the new corpus and retrain the model
    ft_model_path = os.getenv("FT_MODEL_PATH")

    if date.today().weekday() == 3:
        # Try loading saved processed data on old movies
        data_path_5000_proc = os.getenv("DATA_PATH_5000_PROCESSED")
        try:
            movie_desc_5000 = pd.read_csv(data_path_5000_proc)

        # If this processed file doesn't exist yet, create it from the external data file from kaggle
        except FileNotFoundError:
            data_path_5000_ext = os.getenv("DATA_PATH_5000_EXTERNAL")
            movie_desc_5000 = process_kaggle_tmdb_dataset(path_kaggle_file=data_path_5000_ext,
                                                          path_processed_file=data_path_5000_proc)
        # Create the corpus
        data_path_norm_corpus = os.getenv("DATA_PATH_NORM_CORPUS")
        norm_movie_corpus = generate_movie_corpus(old_movies_desc=movie_desc_5000, recent_movies_desc=movie_desc,
                                                  path_normalized_corpus=data_path_norm_corpus)
        tokenized_docs = [doc.split() for doc in norm_movie_corpus]
        # Train the model
        ft_model = train_ft_model(tokenized_docs, ft_model_path)

    # Create the app
    mapbox_access_path = os.getenv("MAPBOX_ACCESS_PATH")
    create_app(cineman_df=cineman_df, movie_desc=movie_desc, MAPBOX_ACCESS_PATH=mapbox_access_path)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
