from rhythmic.general import faultReturnHandler;
from rhythmic.db import SQLiteDB;
from os.path import exists, isdir as isDir;
from datetime import datetime;
from . import configuration;
from . import packFiles;

# var data = 
# {
#     "model_path": window.model_path,
#     "files_tracker": passed_files_data,
#     "modified_files": window.active_version_modified_files,
#     "model_id": window.the_model_id,
#     "new_version_number": parseInt(window.last_version) + 1,
#     "the_active_version": window.the_active_version,
#     "metadata": encodeURI(actual_metadata)
# }

@faultReturnHandler
def createNewVersion(data):

    timestamp = str(datetime.now());


    #=================starting DB work =====================================

    with SQLiteDB(configuration.db_file_name) as db:

        update_model_parameters_request = \
        """
        UPDATE models_table SET 
            last_version_timestamp = '{}', 
            last_version = '{}',
            active_version = '{}'
        WHERE id = '{}';
        """.format(
                            timestamp,
                            data["new_version_number"],
                            data["new_version_number"],
                            data["model_id"]
                        );

        db.execute(update_model_parameters_request);

        add_new_version_request = \
        """
        INSERT INTO versions_table
        (
            model_id,
            version,
            metadata,
            commit_comment,
            created_timestamp
        )
        VALUES ('{}', '{}', '{}', '{}', '{}');
        """.format(
                            data["model_id"],
                            data["new_version_number"],
                            data["metadata"],
                            "Derives from version " + data["the_active_version"] + ".",
                            timestamp
                        );

        new_version_id = db.execute(add_new_version_request);

        record_files_data_request = \
        """
        INSERT INTO files_table
        (
            model_version_id,
            absolute_path,
            file_commit_state,
            last_modified_time,
            is_deployed
        )
        VALUES
        """;

        if len(data["files_tracker"]) > 0:
            files_record_values = "";

            for the_file in data["files_tracker"]:
                file_properties = data["files_tracker"][the_file];
                last_modified_time = file_properties["last_modified_time"];

                if (the_file in data["modified_files"]):
                    file_commit_state = "modified";
                    last_modified_time = data["modified_files"][the_file];

                elif file_properties["file_commit_state"] == "emerged":
                    file_commit_state = "new";
                else:
                    file_commit_state = "same";

                #SQLite has no boolean type, casting int:
                if file_properties["is_deployed"]:
                    is_deployed = 1;
                else:
                    is_deployed = 0;

                files_record_values += "('{}', '{}', '{}', '{}', '{}'), \n".format(new_version_id, the_file, file_commit_state,\
                                                        last_modified_time, is_deployed);

            record_files_data_request +=  files_record_values[:len(files_record_values) -3] + ";"; #truncating `, \n` from the end of request and adding `;`.

            db.execute(record_files_data_request);

    #================= finished DB work =====================================

    model_storage_path = data["model_path"] + "/{}".format(configuration.storage_folder_name);
    if ( (not exists(model_storage_path)) or (not isDir(model_storage_path)) ):
        makeDir(model_storage_path);

    #================= Starting  building ver0 .zip in storage =====================================

    archive_name = model_storage_path + "/model_{}_ver{}.zip".format(data["model_id"], data["new_version_number"]);
    packFiles(data["model_path"], archive_name, data["files_tracker"]);

    #================= Finished building ver0 .zip in storage =====================================

    return "Success";