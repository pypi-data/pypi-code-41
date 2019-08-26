"""
This helper  returns dictionaries of all versions and all the files of all versions of particular model with all the metadata stored.
In other words it returns the whole tree of model related static entities.
"""

from rhythmic.db import SQLiteDB;
from rhythmic.general import faultReturnHandler;
from . import configuration;
from . import modelPropertiesDictionary, versionPropertiesDictionary, filePropertiesDictionary;
from . import scanModelFolder;

def parentFolder(file_path):
    return file_path[:file_path.rfind("/")];

def baseName(file_path):
    return file_path[file_path.rfind("/") + 1:];

def differences(version_files, actual_folder_contents):
    absent_files = {};
    #absent_files = {"folder_path":["file_1_path .. file_n_path"];

    changed_folders = [];
    modified_files = {};

    #first looking for changes relative to tracked data
    for tracked_file in version_files:
        
        change_detected = False;
        parent_folder = parentFolder(tracked_file);

        if tracked_file not in actual_folder_contents:

            if parent_folder not in absent_files:
                absent_files[parent_folder] = [baseName(tracked_file)];
            else:
                absent_files[parent_folder].append(baseName(tracked_file));
            
            change_detected = True;

        else:
            if str(version_files[tracked_file]["last_modified_time"]) != str(actual_folder_contents[tracked_file]["last_modified_time"]):
                change_detected = True;
                modified_files[tracked_file] = actual_folder_contents[tracked_file]["last_modified_time"];

        if change_detected:
            if parent_folder not in changed_folders:
                changed_folders.append(parent_folder);

    #now let us look if there are a new files
    for actual_file in actual_folder_contents:
        parent_folder = parentFolder(actual_file);
        if actual_file not in version_files:
            if parent_folder not in changed_folders:
                changed_folders.append(parent_folder);

    return absent_files, changed_folders, modified_files;

@faultReturnHandler
def modelAllStaticData(model_id):

    all_model_info = \
    {
        "properties": {},
        "model_versions": {}
    };

    with SQLiteDB(configuration.db_file_name) as db:
        
        model_properties = db.execute(
            """
            SELECT * FROM models_table WHERE id = '{}';
            """.format(model_id)
            );

        all_model_info["properties"] = modelPropertiesDictionary(model_properties[0]);

        model_versions = db.execute(
            """
            SELECT * FROM versions_table WHERE model_id = '{}' ORDER BY version DESC;
            """.format(model_id)
            );

        for model_version in model_versions:

            version_properties = versionPropertiesDictionary(model_version);

            version_files = {};

            version_tracked_files = db.execute(
                """
                SELECT * FROM files_table WHERE model_version_id = '{}' ORDER BY absolute_path ASC;
                """.format(version_properties["id"])
                );

            for version_tracked_file in version_tracked_files:

                version_tracked_file_data = filePropertiesDictionary(version_tracked_file);

                version_files_key = version_tracked_file_data["absolute_path"];
                version_files[ version_files_key ] = version_tracked_file_data;

            model_versions_key = version_properties["version"];
            all_model_info["model_versions"][model_versions_key] = \
                {
                    "version_properties": version_properties,
                    "version_files": version_files
                };

            if model_versions_key == all_model_info["properties"]["active_version"]:
                #let us check for changes and prepare them for display, for active modelversion only
                actual_folder_contents = scanModelFolder(all_model_info["properties"]["path"]);

                absent_files, changed_folders, modified_files = differences(version_files, actual_folder_contents);

                all_model_info["model_versions"][model_versions_key].update(
                    {
                        "changed_folders": changed_folders,
                        "absent_files": absent_files,
                        "modified_files": modified_files
                    });

    return all_model_info;