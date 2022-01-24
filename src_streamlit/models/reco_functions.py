from gensim.models import FastText
import pickle
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def train_ft_model(norm_movie_desc):
    tokenized_docs = [doc.split() for doc in norm_movie_desc]
    ft_model = FastText(tokenized_docs, vector_size=300, window=30, min_count=2, workers=4, sg=1, epochs=50)

    return tokenized_docs, ft_model


def averaged_word2vec_vectorizer(corpus, model, num_features):
    """
    Turns word level embeddings into document embeddings
    """
    model_vocab = set(model.wv.index_to_key)

    def average_word_vectors(words, model, vocabulary, num_features):
        feature_vector = np.zeros((num_features,), dtype="float64")
        nwords = 0.

        for word in words:
            if word in vocabulary:
                nwords = nwords + 1.
                feature_vector = np.add(feature_vector, model.wv[word])
        if nwords:
            feature_vector = np.divide(feature_vector, nwords)

        return feature_vector

    features = [average_word_vectors(words=tokenized_sentence, model=model,
                                     vocabulary=model_vocab, num_features=num_features)
                for tokenized_sentence in corpus]

    return np.array(features)


def calc_cosine_similarity(corpus, model, num_features):
    document_vectors = averaged_word2vec_vectorizer(corpus=corpus, model=model, num_features=num_features)
    doc_similarities = pd.DataFrame(cosine_similarity(document_vectors))

    return doc_similarities


def recent_movie_recommender(movie_title, all_movies_desc, recent_movies_desc, similarities_df):
    all_movies = all_movies_desc['original_title'].values
    recent_movies = recent_movies_desc["original_title"].values
    recent_movie_idx = all_movies_desc[all_movies_desc["original_title"].isin(recent_movies)].index
    movie_idx = np.where(all_movies == movie_title)[0][0]
    movie_similarities = similarities_df.iloc[movie_idx].values
    similar_movies = np.argsort(-movie_similarities)
    similar_recent_movies = [index for index in similar_movies if index in recent_movie_idx]
    movie_rec = all_movies[similar_recent_movies][0]
    if movie_rec == movie_title:
        movie_rec = all_movies[similar_recent_movies][1]
    return movie_rec
