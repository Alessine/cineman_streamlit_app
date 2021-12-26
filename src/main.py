#!/usr/bin/env python
# coding: utf-8

import time
import pandas as pd
import streamlit as st
import s3fs
from datetime import date
import pickle

from visualization.cineman_streamlit_app import create_app
import features.corpus_prep as cp
import models.reco_functions as rf


def main():
    # Create connection to AWS S3 Bucket
    # `anon=False` means not anonymous, i.e. it uses access keys to pull data.
    fs = s3fs.S3FileSystem(anon=False)

    # Reading in user-dependent variables: file paths
    data_path_shows = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_showtimes.csv"
    data_path_desc = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_zurich_movie_overviews.csv"

    # Try loading saved data on movies currently running in Zurich
    cineman_df = pd.read_csv(data_path_shows)
    movie_desc = pd.read_csv(data_path_desc)

    # If the model is more than a week old, create the new corpus and retrain the model
    data_path_doc_sims = "s3://zmr-streamlit-aws/models/document_similarities.csv"
    data_path_comb_corpus = "s3://zmr-streamlit-aws/data/processed/comb_movie_corpus.csv"

    if time.time() - fs.modified(data_path_doc_sims).timestamp() > 600:
        # Try loading saved processed data on old movies
        data_path_5000_proc = "s3://zmr-streamlit-aws/data/processed/tmdb_5000_movies_proc.csv"
        try:
            movie_desc_5000 = pd.read_csv(data_path_5000_proc)
        # If this processed file doesn't exist yet, create it from the external data file from kaggle
        except FileNotFoundError:
            data_path_5000_ext = "s3://zmr-streamlit-aws/data/external/tmdb_5000_movies.csv"
            movies_kaggle = pd.read_csv(data_path_5000_ext)
            movie_desc_5000 = cp.process_kaggle_tmdb_dataset(kaggle_file=movies_kaggle)
            movie_desc_5000.to_csv(data_path_5000_proc)

        # Create the corpus
        all_movies_corpus, norm_movie_desc = cp.generate_movie_corpus(old_movies_desc=movie_desc_5000,
                                                                   recent_movies_desc=movie_desc)
        all_movies_corpus.to_csv(data_path_comb_corpus)

        # Tokenize the corpus and train the model
        ft_model_path = "s3://zmr-streamlit-aws/models/fast_text_model.sav"
        tokenized_docs, ft_model = rf.train_ft_model(norm_movie_desc)
        pickle.dump(ft_model, open(ft_model_path, 'wb'))

        # Calculate document vectors and similarities
        doc_similarities = rf.calc_cosine_similarity(corpus=tokenized_docs, model=ft_model, num_features=300)
        doc_similarities.to_csv(data_path_doc_sims)

    else:
        all_movies_corpus = pd.read_csv(data_path_comb_corpus, index_col=0)
        doc_similarities = pd.read_csv(data_path_doc_sims, index_col=0)

    # Create the app
    mapbox_access_token = st.secrets["MAPBOX_ACCESS_TOKEN"]

    create_app(cineman_df=cineman_df, movie_desc=movie_desc, all_movies_desc=all_movies_corpus,
               similarities_df=doc_similarities, MAPBOX_ACCESS_TOKEN=mapbox_access_token)


if __name__ == '__main__':
    main()
