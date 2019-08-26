from . import configuration;
from rhythmic.db import SQLiteDB;
from rhythmic.general import faultReturnHandler;
from .db_record_to_dictionary import modelPropertiesDictionary;

@faultReturnHandler
def getModelsList():

    with SQLiteDB(configuration.db_file_name) as db:
        models_table = db.execute(
            """
            SELECT * FROM models_table WHERE 1 ORDER BY last_version_timestamp DESC;
            """);

    models = [];

    for model in models_table:
        models.append( modelPropertiesDictionary(model) );

    return models;