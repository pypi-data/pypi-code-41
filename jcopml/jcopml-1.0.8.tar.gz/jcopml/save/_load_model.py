import pickle
from warnings import warn


def load_model(model_path):
    """
    Saving object using pickle


    == Example usage ==
    load_model("model/my_file.pkl")


    == Arguments ==
    model_path: string
        a .pkl model file path
    """
    warn("load_model is moved to jcopml.utils in the future version")
    model = pickle.load(open(model_path, "rb"))
    return model
