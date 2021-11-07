import requests
import json
import gzip
import pandas as pd
from urllib.request import urlretrieve
from datetime import date, timedelta, datetime


def fetch_tmdb_movie_ids(TMDB_IDS_FILE_PATH):
    """
    This function downloads the zipped json file from TMDB with the most recent movie IDs in it.
    Then it unzippes the file and stores its contents in a data frame.

    Optional arguments:
    - directory: string, path to the folder where the zipped file from tmdb will be saved, defaults to
        TMDB_IDS_FILE_PATH (user dependent)

    Returns:
    - movie_id_df: pandas dataframe containing the ID and other information on all the tmdb movies.
    """
    # Download the most current file
    current_time = datetime.now()

    # If it's early, need to take the file from yesterday
    if current_time.hour < 10:
        year = str(date.today() - timedelta(days=1))[0:4]
        month = str(date.today() - timedelta(days=1))[5:7]
        day = str(date.today() - timedelta(days=1))[8:10]

    # After 10 o'clock, today's file should be available.
    else:
        year = str(date.today())[0:4]
        month = str(date.today())[5:7]
        day = str(date.today())[8:10]

    path = f"http://files.tmdb.org/p/exports/movie_ids_{month}_{day}_{year}.json.gz"
    urlretrieve(path, TMDB_IDS_FILE_PATH)

    # Unzip the file
    with gzip.GzipFile(TMDB_IDS_FILE_PATH, 'r') as fin:
        json_bytes = fin.read()

        # Format the output into a list of strings
    json_list_of_str = json_bytes.decode().split("\n")

    # Turn the list of strings into a list of dictionaries
    dict_list = []
    for dict_str in json_list_of_str[:-1]:
        real_dict = json.loads(dict_str)
        dict_list.append(real_dict)

    # Convert it to a dataframe
    movie_id_df = pd.DataFrame(dict_list)

    return movie_id_df


def get_specific_movie_ids(TMDB_IDS_FILE_PATH, DATA_PATH_SHOWS, movies_list=None):
    """
    This function takes in a directory, the path to a csv file or a list of movie titles.
    Then it filters the main json file with movie IDs from tmdb to keep only information for those titles that can be matched with
    movies in the list or data frame from the csv file.

    Optional arguments:
    - directory: string, path to the folder where the zipped file from tmdb will be saved, defaults to TMDB_IDS_FILE_PATH (user dependent)
    - csv_path: string, the path to a csv file with movie titles (will be read in), defaults to DATA_PATH_SHOWS (user dependent)
    - movies_list: list, containing the selected movie titles, defaults to None

    Returns:
    - selected_films_df: pandas dataframe with tmdb information on the films that are listed in the csv file or movies list.
    """
    # If a list is provided, use it directly
    if movies_list:
        specific_movies = movies_list

    # Otherwise read in a df from a csv file and create the list
    else:
        specific_movies_df = pd.read_csv(DATA_PATH_SHOWS, index_col=0)
        specific_movies = specific_movies_df["movie"].unique()

    # Download the file with all the movie IDs from tmdb
    tmdb_ids_df = fetch_tmdb_movie_ids(TMDB_IDS_FILE_PATH=TMDB_IDS_FILE_PATH)
    specific_movie_id_df = tmdb_ids_df[tmdb_ids_df["original_title"].isin(specific_movies)].reset_index(drop=True)

    # Some of the movie titles appear more than once with different IDs - need to take only the most recent one (highest popularity score)
    selected_films = []

    for movie in specific_movies:
        same_title = specific_movie_id_df[specific_movie_id_df["original_title"] == movie]
        if not same_title.empty:
            selected_film = same_title[same_title["popularity"] == max(same_title["popularity"])]
            if len(selected_film) == 1:
                selected_films.append(selected_film)
    if selected_films:
        selected_films_df = pd.concat(selected_films).reset_index(drop=True)
    else:
        selected_films_df = pd.DataFrame({"adult": [], "id": [], "original_title": [], "popularity": [], "video": []})

    return selected_films_df


def get_specific_movie_overviews(TMDB_IDS_FILE_PATH, TMDB_CREDENTIALS_PATH, DATA_PATH_SHOWS, DATA_PATH_DESC,
                                 movies_list=None):
    """
    This function takes in a directory, the path to a csv file or a list of movie titles and the path to the tmbd api credentials.
    It downloads and saves the main json file with movie IDs from tmdb in the specified directory.
    Then it filters the main file to keep only information for those titles that can be matched with movies in the list or data
    frame from the csv file. Finally it requests the movie taglines and overviews via the tmdb api.

    Optional arguments:
    - directory: string, path to the folder where the zipped file from tmdb will be saved, defaults to ../data/raw/tmdb_id_file.gz
    - csv_path: string, the path to a csv file with movie titles (will be read in), defaults to ../data/raw/specific_movies.csv
    - movies_list: list, containing the selected movie titles, defaults to None
    - credentials_path: string, path to the file in which the tmdb api credentials are saved, defaults to ../tmdb_credentials.yml.

    Returns:
    - movies_overviews_df: pandas dataframe with information on the selected movies, including the overviews
    """
    # Load the DF with the specified movie titles and IDs
    selected_films_df = get_specific_movie_ids(TMDB_IDS_FILE_PATH=TMDB_IDS_FILE_PATH, DATA_PATH_SHOWS=DATA_PATH_SHOWS,
                                               movies_list=movies_list)

    # load the API credentials
    key_yml = json.load(open(TMDB_CREDENTIALS_PATH))
    tmdb_api_key = key_yml["api_key"]

    # take only the movie ids column
    current_ids = selected_films_df["id"]
    taglines = []
    overviews = []
    movie_genres = []

    # request info for each movie and store the movie overviews in a list
    for movie_id in current_ids:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key="
        req = requests.get(url + tmdb_api_key)
        movie_json = req.json()
        taglines.append(movie_json["tagline"])
        overviews.append(movie_json["overview"])
        genres = []
        for genre in movie_json["genres"]:
            genres.append(genre["name"])
        genre_string = " ".join(genres)
        movie_genres.append(genre_string)

    # create the new dataframe with the movie overviews column
    movies_overviews_df = selected_films_df
    movies_overviews_df["tagline"] = taglines
    movies_overviews_df["overview"] = overviews
    movies_overviews_df["genres_string"] = movie_genres

    movies_overviews_df.to_csv(DATA_PATH_DESC)
