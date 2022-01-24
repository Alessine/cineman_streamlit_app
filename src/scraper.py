#!/usr/bin/env python
# coding: utf-8

import s3fs
from dotenv import find_dotenv, load_dotenv
import os
from datetime import date
import logging
import time
import pandas as pd
import pickle

import data.cineman_scraping as cs
from data.tmdb_api import get_specific_movie_overviews
import features.corpus_prep as cp
import models.reco_functions as rf


def scraper():
    # Start logging
    logger = logging.getLogger(__name__)

    # Defining file paths
    data_path_shows = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_showtimes.csv"
    data_path_desc = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_zurich_movie_overviews.csv"
    tmdb_ids_file_path = "s3://zmr-streamlit-aws/data/external/tmdb_id_file.gz"

    # Getting credentials
    tmdb_credentials_path = os.getenv("TMDB_CREDENTIALS_PATH")
    logger.info('TMDB credentials path fetched')

    # Create connection to AWS S3 Bucket
    fs = s3fs.S3FileSystem(anon=False)

    # Scraping the most recent data and saving it
    content = cs.scrape_cineman(cities=("Zürich"))
    movie_program_df = cs.format_cineman_content(html_content=content)
    cineman_df = cs.add_theatre_coordinates(showtimes_df=movie_program_df)
    cineman_df.to_csv(data_path_shows)
    logger.info('First data file saved to bucket')

    # Requesting movie overviews via the tmdb api and saving them
    movie_desc = get_specific_movie_overviews(TMDB_IDS_FILE_PATH=tmdb_ids_file_path,
                                              TMDB_CREDENTIALS_PATH=tmdb_credentials_path,
                                              DATA_PATH_SHOWS=data_path_shows,
                                              movies_list=None)
    movie_desc.to_csv(data_path_desc)
    logger.info('Second data file saved to bucket')

    # Create the new corpus and retrain the model
    data_path_doc_sims = "s3://zmr-streamlit-aws/models/document_similarities.csv"
    data_path_comb_corpus = "s3://zmr-streamlit-aws/data/processed/comb_movie_corpus.csv"


    #logger.info('Retraining model')
    # Try loading saved processed data on old movies
    data_path_750_proc = "s3://zmr-streamlit-aws/data/processed/tmdb_750_movies_proc.csv"
    try:
        movie_desc_750 = pd.read_csv(data_path_750_proc)
    # If this processed file doesn't exist yet, create it from the external data file from kaggle
    except FileNotFoundError:
        data_path_750_ext = "s3://zmr-streamlit-aws/data/external/tmdb_750_movies.csv"
        movies_kaggle = pd.read_csv(data_path_750_ext)
        movie_desc_750 = cp.process_kaggle_tmdb_dataset(kaggle_file=movies_kaggle)
        movie_desc_750.to_csv(data_path_750_proc)

    # Create the corpus
    all_movies_corpus, norm_movie_desc = cp.generate_movie_corpus(old_movies_desc=movie_desc_750,
                                                               recent_movies_desc=movie_desc)
    all_movies_corpus.to_csv(data_path_comb_corpus)

    # Tokenize the corpus and train the model
    ft_model_path = "s3://zmr-streamlit-aws/models/fast_text_model.sav"
    tokenized_docs, ft_model = rf.train_ft_model(norm_movie_desc)
    logger.info("Model training finished")

    #pickle.dump(ft_model, fs.open(ft_model_path, 'wb'))
    #logger.info('Retrained model saved to bucket')

    # Calculate document vectors and similarities
    doc_similarities = rf.calc_cosine_similarity(corpus=tokenized_docs, model=ft_model, num_features=300)
    doc_similarities.to_csv(data_path_doc_sims)
    logger.info('Document similarity matrix saved to bucket')


if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)

    load_dotenv(find_dotenv())

    scraper()

