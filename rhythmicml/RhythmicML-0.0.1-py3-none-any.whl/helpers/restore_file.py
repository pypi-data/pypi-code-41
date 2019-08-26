from rhythmic.general import faultReturnHandler;
from rhythmic.db import SQLiteDB;
from . import configuration, scanFolder, unpackSingleFile;

def restoreFile(data):
    """
    var data = 
    {
        "file_absolute_path": absolute_path,
        "model_path": window.model_path,
        "model_id": window.the_model_id,
        "version_number": window.active_version_number,
        "version_id": window.active_version_id
    }
    """

    model_version_archive_file_name = "{}/{}/model_{}_ver{}.zip".\
    format(
                    data["model_path"],
                    configuration.storage_folder_name,
                    data["model_id"],
                    data["version_number"]
                );

    unpackSingleFile(model_version_archive_file_name, data["file_absolute_path"], data["model_path"]);

    #after unpacking we have to update last_modified_time for UI would not mark that file as modified

    base_index = data["file_absolute_path"].rfind("/");
    file_containing_folder = data["file_absolute_path"][: base_index + 1]

    folder_contents = scanFolder(file_containing_folder);

    if data["file_absolute_path"] in folder_contents:
        with SQLiteDB(configuration.db_file_name) as db:
            db.execute(
                """
                UPDATE files_table SET last_modified_time ='{}' WHERE model_version_id = '{}' AND absolute_path = '{}';
                """.format(
                                    folder_contents[ data["file_absolute_path"] ]["last_modified_time"],
                                    data["version_id"],
                                    data["file_absolute_path"]
                                )
                );


    return "Success";
