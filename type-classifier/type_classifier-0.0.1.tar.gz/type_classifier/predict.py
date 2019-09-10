import pandas as pd
import pickle
import os


def load_model(model_file='model_trained.sav'):
    this_dir, this_filename = os.path.split(__file__)
    data_path = os.path.join(this_dir, model_file)
    return pickle.load(open(data_path, 'rb'))


def preprocess_vector(c_vector):
    # print(c_vector)
    c_vector = [
        i for i in c_vector.replace("\n", "").replace("[", "").replace(
            "]", "").replace(",", "").split(' ') if i != ''
    ]
    c_vector = [float(i) for i in c_vector]

    return pd.Series([c_vector]).apply(pd.Series)


def predict_proba_category(c_vector):
    """

    Predict the category of a company from its c_vector

    :param c_vector: vector of size 512 as a string
    :return: probability of being a product company
    """

    model = load_model()

    vector_description = preprocess_vector(c_vector)

    return model.predict_proba(vector_description)[0][1]


def predict_category(c_vector):
    """

    Predict the category of a company from its c_vector

    :param c_vector: vector of size 512 as a string
    :return: category (S or P)
    """

    model = load_model()

    vector_description = preprocess_vector(c_vector)

    return model.predict(vector_description)[0]

