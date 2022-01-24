Zurich Movie Recommender
==============================

![](reports/theatre_seats.jpg)
Foto by [Denise Jans](https://unsplash.com/@dmjdenise)

Purpose
---------
I love going to the theatre to watch a movie, especially on a rainy weekend (which is most weekends in Zurich...). But more often than not, I found myself not being able to choose a movie out of all the ones being shown. Often I would end up just watching the most well-known big budget movie currently on, because I didn't want to spend time looking through the trailers of all the smaller alternative productions, but then I felt like I was missing out on too much of the diversity of movies available. Over the past few months, I built this movie recommender to solve this problem for me.

How it works
----------
This Streamlit app takes as an input the name of the user's favorite movie. It then compares the description for that movie (from tmdb) with the descriptions of all the movies that are currently running in Zurich. It recommends the most similar one and lists all the showtimes for the current date (scraped from cineman.ch).

In order to compare the similarity of the movie descriptions, the app uses a FastText model to create document-level embeddings. All of these document vectors are then compared with each other and a similarity score is calculated based on the cosine similarity of the vectors. The similarity scores are stored in a matrix, which is used when making a recommendation.

Project Organization
------------
Here's how I've organized the project files:

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources. [not being versioned]
    │   ├── processed      <- The final, canonical data sets for modeling. [not being versioned]
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained or pretrained models, similarity matrices
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is the date when I started working 
    │                         on it (YYMMDD), and a short `_` delimited description, e.g.
    │                         `211010_cineman_scraping.ipynb`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├── cineman_scraping.py
    │   │   └── tmdb_api.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── corpus_prep.py
    │   │
    │   ├── models         <- Scripts to train models and generate the similarity matrix
    │   │   └── reco_functions.py
    │   │
    │   └── visualization  <- Scripts to create visualizations and the streamlit app
    │       ├── cineman_streamlit_app.py
    │       └── plotting_functions.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
