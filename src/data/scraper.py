#!/usr/bin/env python
# coding: utf-8

import s3fs
from dotenv import find_dotenv, load_dotenv
import os
from datetime import date

import cineman_scraping as cs
from tmdb_api import get_specific_movie_overviews


def scraper():
    # Defining file paths
    data_path_shows = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_showtimes.csv"
    data_path_desc = f"s3://zmr-streamlit-aws/data/raw/{date.today()}_zurich_movie_overviews.csv"
    tmdb_ids_file_path = "s3://zmr-streamlit-aws/data/external/tmdb_id_file.gz"

    # Getting credentials
    tmdb_credentials_path = os.getenv("TMDB_CREDENTIALS_PATH")

    # Create connection to AWS S3 Bucket
    fs = s3fs.S3FileSystem(anon=False)

    # Scraping the most recent data and saving it
    content = cs.scrape_cineman(cities=("Zürich"))
    movie_program_df = cs.format_cineman_content(html_content=content)
    cineman_df = cs.add_theatre_coordinates(showtimes_df=movie_program_df)
    cineman_df.to_csv(data_path_shows)

    # Requesting movie overviews via the tmdb api and saving them
    movie_desc = get_specific_movie_overviews(TMDB_IDS_FILE_PATH=tmdb_ids_file_path,
                                              TMDB_CREDENTIALS_PATH=tmdb_credentials_path,
                                              DATA_PATH_SHOWS=data_path_shows,
                                              movies_list=None)
    movie_desc.to_csv(data_path_desc)


if __name__ == '__main__':
    load_dotenv(find_dotenv())
    scraper()
