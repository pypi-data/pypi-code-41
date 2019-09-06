# libs
import joblib
from sklearn.pipeline import Pipeline

# packages
from ukchurn_classification_model.config import config


def remove_old_pipelines(*, files_to_keep) -> None:
    """
    Remove old model pipelines.
    This is to ensure there is a simple one-to-one
    mapping between the package version and the model
    version to be imported and used by other applications.
    """

    for model_file in config.TRAINED_MODEL_DIR.iterdir():
        if model_file.name not in [files_to_keep, '__init__.py']:
            model_file.unlink()


def save_pipeline(*, pipeline_to_persist) -> None:
    """Persist the pipeline.
    Saves the versioned model, and overwrites any previous
    saved models
    """

    save_path = config.TRAINED_MODEL_DIR / config.PIPELINE_NAME
    remove_old_pipelines(files_to_keep=config.PIPELINE_NAME)
    joblib.dump(pipeline_to_persist, save_path)

    print('Saved pipeline: ')
    print(pipeline_to_persist)


def load_pipeline(*, file_name: str) -> Pipeline:
    """Load a persisted pipeline"""

    file_path = config.TRAINED_MODEL_DIR / file_name
    saved_pipeline = joblib.load(filename=file_path)
    return saved_pipeline
