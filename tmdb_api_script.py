import requests
import json
import gzip
import pandas as pd
import urllib.request
from datetime import date

# Get the ID file from tmdb
tmdb_id_file = urllib.request.URLopener()
tmdb_id_file.retrieve("http://files.tmdb.org/p/exports/movie_ids_10_09_2021.json.gz", "./data/tmdb_id_file.gz")

# Unzip it and store the string in a list of strings
with gzip.GzipFile("./data/tmdb_id_file.gz", 'r') as fin:
    json_bytes = fin.read()
json_list_of_str = json_bytes.decode().split("\n")

# Turn the list of strings into a list of dictionaries
dict_list = []
for dict_str in json_list_of_str[:-1]:
    real_dict = json.loads(dict_str)
    dict_list.append(real_dict)

# Convert it to a dataframe
movie_id_df = pd.DataFrame(dict_list)

# load the API credentials
key_yml = json.load(open("./tmdb_credentials.yml"))
tmdb_api_key = key_yml["api_key"]

# read in the info on movies currently playing in Zurich
cineman_df = pd.read_csv(f"./data/2021-09-24_showtimes_zurich.csv", index_col=0)

# Merge the tmdb id with the movie info
# it fails to match some of the titles but we still want to keep the cineman info
cineman_tmdb_df = pd.merge(left=cineman_df, right=movie_id_df,
                           left_on="movie", right_on="original_title", how="left")

# then request the overview for all the matched movies
current_ids = cineman_tmdb_df["id"].dropna().astype("int")
overviews = []

for movie_id in current_ids:
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key="
    req = requests.get(url + tmdb_api_key)
    movie_json = req.json()
    overviews.append(movie_json["overview"])

# Create dataframe with id and overview
overviews_df = pd.DataFrame({"id": current_ids, "overview": overviews})

# then merge everything
cineman_tmdb_df = pd.merge(left=cineman_tmdb_df, right=overviews_df, on="id", how="left")
cineman_tmdb_df.to_csv(f"data/{date.today()}_showtimes_zurich_tmdb_overviews.csv")
