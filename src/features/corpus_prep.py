import pandas as pd
import json
import numpy as np
import re
import contractions
import nltk


# Helper Functions
def get_movie_genres(movies_df):
    """
    This function takes in a dataframe with information on movies from tmdb and creates a new column with the genre
    strings, which were before nested within the json string.

    Required arguments:
    - movies_df: a dataframe with movie information

    Returns:
    - movie_genres: list of strings, contains movie genres for each movie
    """
    movie_genres = []
    for i in range(len(movies_df)):
        genre_list = json.loads(movies_df.genres[i])
        genres = []
        for genre in genre_list:
            genres.append(genre["name"])

        genre_string = " ".join(genres)
        movie_genres.append(genre_string)
    return movie_genres


def process_kaggle_tmdb_dataset(path_kaggle_file, path_processed_file):
    """
    This function takes in the file path to the tmdb 5000 movies file from kaggle and adds the genres_string column.

    Required arguments:
    - path_kaggle_file: string, the path to the data file from kaggle
    - path_processed_file: string, the path where the processed file will be saved
    """
    movie_desc_5000 = pd.read_csv(path_kaggle_file)
    movie_desc_5000["genres_string"] = get_movie_genres(movie_desc_5000)
    movie_desc_5000 = movie_desc_5000.sort_values("popularity", ascending=False).drop_duplicates("original_title"
                                                                                                 ).reset_index()
    movie_desc_5000.to_csv(path_processed_file)
    return movie_desc_5000


def prepare_movie_descriptions(df):
    df_2 = df.copy()
    df_2 = df_2.loc[df_2["overview"].notna()]
    df_2["tagline"] = df_2["tagline"].fillna("")
    df_2["genres_string"] = df_2["genres_string"].fillna("")
    df_2["description"] = df_2["tagline"] + " " + df_2["overview"] + " " + df_2["genres_string"]
    df_2 = df_2[["original_title", "description"]]
    return df_2


stop_words_eng = nltk.corpus.stopwords.words('english')


def normalize_document(doc, stop_words=stop_words_eng):
    # remove special characters
    doc = re.sub(r'[^a-zA-Z0-9\s]', '', doc, flags=re.I|re.A)
    # lower case
    doc = doc.lower()
    # strip whitespaces
    doc = doc.strip()
    # fix contractions
    doc = contractions.fix(doc)
    # tokenize document
    tokens = nltk.word_tokenize(doc)
    #filter stopwords out of document
    filtered_tokens = [token for token in tokens if token not in stop_words]
    # re-create document from filtered tokens
    doc = ' '.join(filtered_tokens)
    return doc


normalize_corpus = np.vectorize(normalize_document)


def generate_movie_corpus(old_movies_desc, recent_movies_desc, path_combined_corpus):
    old_movies_desc_corp = prepare_movie_descriptions(old_movies_desc)
    recent_movies_desc_corp = prepare_movie_descriptions(recent_movies_desc)
    all_movies_corpus = pd.concat([old_movies_desc_corp, recent_movies_desc_corp]).drop_duplicates(
        "original_title", keep="last").reset_index(drop=True)
    all_movies_corpus.to_csv(path_combined_corpus)
    norm_movie_desc = normalize_corpus(list(all_movies_corpus["description"]))
    return all_movies_corpus, norm_movie_desc
