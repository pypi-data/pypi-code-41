from rhythmic.general import faultReturnHandler;
from rhythmic.db import SQLiteDB;
from . import configuration, scanFolder;
from os import remove, rmdir as rmDir;

@faultReturnHandler
def removeModel(data):
    """
    var data_for_helper =
    {
        "model_id": the_id,
        "model_path": model_path
    }
    """

    with SQLiteDB(configuration.db_file_name) as db:

        db.execute("PRAGMA foreign_keys = ON;");
        db.execute(
            """
            DELETE FROM models_table WHERE id = '{}';
            """.format(
                                data["model_id"]
                            )
            );

    model_storage_path = data["model_path"] + "/{}".format(configuration.storage_folder_name);

    versions_packages = scanFolder(model_storage_path, look_level_above = False);

    for version_package in versions_packages:
             remove(version_package);

    rmDir(model_storage_path);

    return "Success";
