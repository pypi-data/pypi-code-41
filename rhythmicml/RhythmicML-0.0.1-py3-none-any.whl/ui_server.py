from flask import Flask, render_template as renderTemplate, request;
from functools import wraps;
from urllib.parse import unquote;
import json;
from os import remove;
from . import helpers;

app = Flask(__name__);

#==========================================================================
#====================      DECORATORS     =========================================
#==========================================================================
def checkPost(entry_point):

    @wraps(entry_point)
    def wrapper(*args, **kwargs):
        if request.method == "POST":

            return entry_point(*args, **kwargs);

        else:

            random_string_html = \
            """
            <div align = "center" style = "padding: 32px;">
            <h1>
            {}
            </h1>
            <a href = "/">main page</a>
            </div>
            """.format( helpers.randomString() );

            return random_string_html;

    return wrapper;


#==========================================================================

#==========================================================================
#====================      UI PAGES      ============================================
#==========================================================================
@app.route("/")
def index():
    """
    On the root page models catalogue is displayed and managed.
    """
    models_list = helpers.getModelsList();
    
    #print("{}/{}".format(__name__, "index"));
    #print(models_list);

    return renderTemplate("index.html", title = "Catalogue", ui_caption = "Catalogue", models_list = models_list);

#==========================================================================

#==========================================================================

@app.route("/dashboard")
@app.route("/dashboard/<model_id>")
def dashboard(model_id = None):
    """
    /dashboard/<model_id>
    This is a particular model's dashboard, rendered with id.
    """

    model_static_data = helpers.modelAllStaticData(model_id);

    #print("{}/{}".format(__name__, "dashboard"));
    # print(model_static_data);

    return renderTemplate("dashboard.html", title = "Model Dashboard", ui_caption = "Model Dashboard", model_static_data = model_static_data);
#==========================================================================

#==========================================================================
#====================      HELPERS      ============================================
#==========================================================================

@app.route("/helpers/folders", methods = ["POST", "GET"])
@app.route("/helpers/folders/<template_modificator>", methods = ["POST", "GET"])
@checkPost
def helperFolders(template_modificator = "catalogue"):
    """
    /heplers/folders/<template_modificator>
    receives local folder path in POST request;
    shows the folder contents, if accessible for the user.
    template_modificator chooses the template to render the content into.
    """

    folder_contents_templates = {
        "catalogue": "folder_contents_catalogue.html",
        "dashboard": "folder_contents_dashboard.html"
    };

    data_json = request.data.decode();
    data = json.loads(data_json);

    the_folder = data["the_folder"];

    if "look_level_above" in data:
        look_level_above = data["look_level_above"];
    else:
        look_level_above = True;

    folder_contents = helpers.scanFolder(the_folder, look_level_above = look_level_above);

    if folder_contents.__class__ == str: #the decorator returns an error message, if folderScan() execution fails
        return folder_contents;

    return renderTemplate(folder_contents_templates[template_modificator], folder_contents = folder_contents, the_folder = the_folder);
#==========================================================================

#==========================================================================
@app.route("/helpers/folder_name_to_model_name", methods = ["POST", "GET"])
@checkPost
def helperFolderNameToModelName():
    """
    /helpers/foldername2modelname
    receives a path user picked path
    and returns a unique model name suggestion.
    """

    the_folder = request.data.decode();

    folder_base_name = helpers.getNameFromPath(the_folder);
    suggested_model_name = helpers.uniqueName(folder_base_name);

    return suggested_model_name;
#==========================================================================

#==========================================================================
@app.route("/helpers/add_new_model", methods = ["POST", "GET"])
@checkPost
def addModel():

    # model_name = request.data.model_name.decode();
    # the_folder = request.data.model_path.decode();

    data_json = request.data.decode();
    data = json.loads(data_json);

    new_model_name = data["model_name"];
    new_model_path = data["model_path"].replace(" ", "\\ ");

    execution_status = helpers.addNewModel(new_model_name, new_model_path);

    return execution_status;

#==========================================================================

#==========================================================================

@app.route("/helpers/confirmation_dialogue", methods = ["POST", "GET"])
@checkPost
def renderConfirmationDialogue():

    data_json = request.data.decode();
    data = json.loads(data_json);
# confirmation dialogue parameters are the following (passed as an object):
# confirmation_message - string, the statement to confirm
# helper_url - string, an url to request if confirmation is positive
# data_for_helper - string, data to send with that request
# confirmation_result - string: 
#      "refresh" - call asyncPostRequestWithRefresh
#      "value" - call asyncPostRequest(..., to_innerHTML = false)
#      "html" - call regular asyncPostRequest();
# result_element_id - string, dom element id to use in "value" and "html" cases

    return renderTemplate("confirmation_dialogue.html", confirmation_dialogue_parameters = data);


#==========================================================================

#==========================================================================

@app.route("/helpers/set_new_deploy_destination", methods = ["POST", "GET"])
@checkPost
def setNewDeployDestination():
    
    data_json = request.data.decode();
    data = json.loads(data_json);

    return helpers.setNewModelDeployDestination(data["the_model_id"], data["new_deploy_destination"]);

#==========================================================================

#==========================================================================

@app.route("/helpers/new_metadata_and_deployables", methods = ["POST", "GET"])
@checkPost
def updateActiveVersionMetadataAndDeployables():

    data_json = request.data.decode();
    data = json.loads(data_json);
    data["actual_metadata"] = unquote(data["actual_metadata"]);

    return helpers.updateMetadataAndDeployables(data);

#==========================================================================

#==========================================================================

@app.route("/helpers/create_new_version", methods = ["POST", "GET"])
@checkPost
def createNewVersion():

    data_json = request.data.decode();
    data = json.loads(data_json);
    data["metadata"] = unquote(data["metadata"]); 

    return helpers.createNewVersion(data);


#==========================================================================

#==========================================================================

@app.route("/helpers/change_active_version", methods = ["POST", "GET"])
@checkPost
def changeActiveVersion():

    data_json = request.data.decode();
    data = json.loads(data_json);

    return helpers.setModelVersionActive(data);

#==========================================================================

#==========================================================================

@app.route("/helpers/restore_file", methods = ["POST", "GET"])
@checkPost
def restoreFile():
    data_json = request.data.decode();
    data = json.loads(data_json);

    return helpers.restoreFile(data);
#==========================================================================

#==========================================================================

@app.route("/helpers/delete_file", methods = ["POST", "GET"])
@checkPost
def deleteFile():
    file_path = request.data.decode();

    try:
        remove(file_path);
    except Exception as error_message:
        return "Fault: {}".format(error_message);
        
    return "Success";
#==========================================================================

#==========================================================================

@app.route("/helpers/remove_model", methods = ["POST", "GET"])
@checkPost
def removeModel():

    data_json = request.data.decode();
    data = json.loads(data_json)

    return helpers.removeModel(data);


#==========================================================================
#==========================================================================
#==========================================================================

def runUI(app, host = helpers.configuration.host, port = helpers.configuration.port):
    """
    run_ui(app, host = host, port = port):  
    app is a Flask app
    """

    app.run(debug = True, host = host, port = port);

    return True;

if __name__ == "__main__":

    runUI(app);
