from gensim.models import FastText
import pickle


def train_ft_model(tokenized_docs, ft_model_path):
    ft_model = FastText(tokenized_docs, vector_size=300, window=30, min_count=2, workers=4, sg=1, epochs=50)
    pickle.dump(ft_model, open(ft_model_path, 'wb'))
    return ft_model

