#!/usr/bin/env python
# coding: utf-8

import os
import time
from dotenv import find_dotenv, load_dotenv
import pandas as pd
import streamlit as st
import s3fs
from datetime import date

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

    if time.time() - fs.modified(data_path_doc_sims).timestamp() > 600000:
        # Try loading saved processed data on old movies
        data_path_5000_proc = "s3://zmr-streamlit-aws/data/processed/tmdb_5000_movies_proc.csv"
        try:
            movie_desc_5000 = pd.read_csv(data_path_5000_proc)
        # If this processed file doesn't exist yet, create it from the external data file from kaggle
        except FileNotFoundError:
            data_path_5000_ext = "s3://zmr-streamlit-aws/data/external/tmdb_5000_movies.csv"
            movie_desc_5000 = cp.process_kaggle_tmdb_dataset(path_kaggle_file=data_path_5000_ext,
                                                          path_processed_file=data_path_5000_proc)
        # Create the corpus
        all_movies_corpus, norm_movie_desc = cp.generate_movie_corpus(old_movies_desc=movie_desc_5000,
                                                                   recent_movies_desc=movie_desc,
                                                                   path_combined_corpus=data_path_comb_corpus)
        tokenized_docs = [doc.split() for doc in norm_movie_desc]
        # Train the model
        ft_model_path = "s3://zmr-streamlit-aws/models/fast_text_model.sav"
        ft_model = rf.train_ft_model(tokenized_docs, ft_model_path)
        # Average the word vectors to get document vectors
        doc_vecs_ft = rf.averaged_word2vec_vectorizer(tokenized_docs, ft_model, 300)
        # Calculate document similarities
        doc_similarities = rf.calc_cosine_similarity(document_vectors=doc_vecs_ft, path_doc_sims=data_path_doc_sims)

    else:
        all_movies_corpus = pd.read_csv(data_path_comb_corpus, index_col=0)
        doc_similarities = pd.read_csv(data_path_doc_sims, index_col=0)

    # Create the app
    # mapbox_access_token = st.secrets["MAPBOX_ACCESS_TOKEN"]
    mapbox_access_path = os.getenv("MAPBOX_ACCESS_PATH")
    mapbox_access_token = open(mapbox_access_path).read()

    create_app(cineman_df=cineman_df, movie_desc=movie_desc, all_movies_desc=all_movies_corpus,
               similarities_df=doc_similarities, MAPBOX_ACCESS_TOKEN=mapbox_access_token)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    main()
