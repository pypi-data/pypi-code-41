from rhythmic.general import faultReturnHandler;
from rhythmic.db import SQLiteDB;
from . import configuration;

@faultReturnHandler
def updateMetadataAndDeployables(data):

    with SQLiteDB(configuration.db_file_name) as db:
        if data["metadata_changed"]:
            db.execute("UPDATE versions_table SET metadata = '{}' WHERE id='{}';".format(data["actual_metadata"], data["active_version_id"]));

        if data["deployables_changed"]:
            for item in data["changed_items"]:
                #SQLite has no boolean types:
                if data["changed_items"][item]:
                    is_deployed = 1;
                else:
                    is_deployed = 0;

                db.execute("UPDATE files_table SET is_deployed = '{}' WHERE id = '{}';".format(is_deployed, item));


    return "Success";