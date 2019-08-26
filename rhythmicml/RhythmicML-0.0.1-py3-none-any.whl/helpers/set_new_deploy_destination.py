from rhythmic.general import faultReturnHandler;
from rhythmic.db import SQLiteDB;
from . import configuration;

@faultReturnHandler
def setNewModelDeployDestination(model_id, new_deploy_destionation):
    with SQLiteDB(configuration.db_file_name) as db:
        db.execute("UPDATE models_table SET deploy_destination = '{}' WHERE id = '{}';".format(new_deploy_destionation, model_id));

    return "Success";