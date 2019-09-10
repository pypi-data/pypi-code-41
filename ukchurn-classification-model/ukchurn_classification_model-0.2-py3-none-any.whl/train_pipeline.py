# libs
import pandas as pd
from sklearn.model_selection import train_test_split

# packages
from ukchurn_classification_model.config import config
from ukchurn_classification_model import pipeline
from ukchurn_classification_model.data_management.pipeline_management import save_pipeline


def run_training() -> None:
    """Train and save model pipeline"""

    # read training data
    data = pd.read_csv(filepath_or_buffer=config.GLOBAL_DATA_FILE)

    # divide train and test
    X_train, X_test, y_train, y_test = train_test_split(
        data[config.FEATURES],
        data[config.TARGET],
        test_size=0.2,
        random_state=0)

    # save train and test in datasets directory
    train = pd.concat([X_train, y_train], axis=1)
    train.to_csv(path_or_buf=config.TRAINING_DATA_FILE, index=False)
    print(f'Saved train set {train.shape}')

    test = pd.concat([X_test, y_test], axis=1)
    test.to_csv(path_or_buf=config.TESTING_DATA_FILE, index=False)
    print(f'Saved train set {test.shape}')

    # fit machine learning pipeline
    pipeline.churn_pipeline.fit(X_train, y_train)

    # save pipeline
    save_pipeline(pipeline_to_persist=pipeline.churn_pipeline)


if __name__ == '__main__':
    run_training()