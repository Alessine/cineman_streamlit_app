#!/usr/bin/env python
# coding: utf-8

#import time
import pandas as pd
from dotenv import find_dotenv, load_dotenv
import os
#import streamlit as st
#import s3fs
from datetime import date
#import pickle

from visualization.cineman_streamlit_app import create_app
#import features.corpus_prep as cp
#import models.reco_functions as rf

# TODO: write some unit tests

def main():
    # Create connection to AWS S3 Bucket
    # `anon=False` means not anonymous, i.e. it uses access keys to pull data.
  #  fs = s3fs.S3FileSystem(anon=False)

    # Defining the file paths
    data_path_shows = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_showtimes.csv"
    data_path_desc = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_zurich_movie_overviews.csv"
    data_path_doc_sims = "s3://zmr-streamlit-aws/models/document_similarities.csv"
    data_path_comb_corpus = "s3://zmr-streamlit-aws/data/processed/comb_movie_corpus.csv"

    # Load saved data on movies currently running in Zurich
    cineman_df = pd.read_csv(data_path_shows)
    movie_desc = pd.read_csv(data_path_desc)

    # Load the full movies corpus and document similarity matrix
    all_movies_corpus = pd.read_csv(data_path_comb_corpus, index_col=0)
    doc_similarities = pd.read_csv(data_path_doc_sims, index_col=0)

    # Create the app
 #   mapbox_access_token = st.secrets["MAPBOX_ACCESS_TOKEN"]
    mapbox_access_path = os.getenv("MAPBOX_ACCESS_PATH")
    mapbox_access_token = open(mapbox_access_path).read()

    create_app(cineman_df=cineman_df, movie_desc=movie_desc, all_movies_desc=all_movies_corpus,
               similarities_df=doc_similarities, MAPBOX_ACCESS_TOKEN=mapbox_access_token)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
