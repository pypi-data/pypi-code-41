from rhythmic.general import faultReturnHandler;

@faultReturnHandler
def modelPropertiesDictionary(sql_raw_list):
    """
    modelPropertiesDictionary(sql_raw_list)
    transforms a row gotten via SQL request (list), to a dictionary

    affects .get_models_list.py
    """
    
    properties_dictionary = \
    {
        "id": sql_raw_list[0],
        "name": sql_raw_list[1],
        "path": sql_raw_list[2],
        "last_version_timestamp": sql_raw_list[3],
        "last_version": sql_raw_list[4],
        "active_version": sql_raw_list[5],
        "deploy_destination": sql_raw_list[6],
        "deploy_status": sql_raw_list[7]
    };

    return properties_dictionary;


@faultReturnHandler
def versionPropertiesDictionary(sql_raw_list):
    """
    versionPropertiesDictionary(sql_raw_list)
    transforms a row gotten via SQL request (list), to a dictionary
    """
    
    properties_dictionary = \
    {
        "id": sql_raw_list[0],
        "model_id": sql_raw_list[1],
        "version": sql_raw_list[2],
        "metadata": sql_raw_list[3],
        "commit_comment": sql_raw_list[4],
        "created_timestamp": sql_raw_list[5]
    }

    return properties_dictionary;

@faultReturnHandler
def filePropertiesDictionary(sql_raw_list):
    """
    filePropertiesDictionary(sql_raw_list)
    transforms a row gotten via SQL request (list), to a dictionary
    """

    #SQLite does not have boolean, so here's type casting needed
    if (sql_raw_list[5] == 0):
        is_deployed = False;
    else:
        is_deployed = True;

    properties_dictionary = \
    {
        "id": sql_raw_list[0],
        "model_version_id": sql_raw_list[1],
        "absolute_path": sql_raw_list[2],
        "file_commit_state": sql_raw_list[3],
        "last_modified_time": sql_raw_list[4],
        "is_deployed": is_deployed
    }

    return properties_dictionary;