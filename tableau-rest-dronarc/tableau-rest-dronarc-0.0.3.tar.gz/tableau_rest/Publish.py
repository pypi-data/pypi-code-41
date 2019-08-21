from tableau_rest import Tools
from tableau_rest import Auth
import sys
import requests  # Contains methods used to make HTTP requests
import os
import math
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

# For when a workbook is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB


def start_upload_session(server, auth_token, site_id):
    """
    Creates a POST request that initiates a file upload session.

    'server'        specified server address
    'auth_token'    authentication token that grants user access to API calls
    'site_id'       ID of the site that the user is signed into
    Returns a session ID that is used by subsequent functions to identify the upload session.
    """
    url = server + "/api/{0}/sites/{1}/fileUploads".format(Tools.VERSION, site_id)
    server_response = requests.post(url, headers={'x-tableau-auth': auth_token})
    Tools.check_status(server_response, 201)
    xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
    return xml_response.find('t:fileUpload', namespaces=Tools.XMLNS).get('uploadSessionId')


def get_project_id(server, project_name, auth_token, site_id):
    """
    Returns the project ID for the project on the Tableau server.

    'server'        specified server address
    'auth_token'    authentication token that grants user access to API calls
    'site_id'       ID of the site that the user is signed into
    """
    page_num, page_size = 1, 1000  # Default paginating values

    # Builds the request
    url = server + "/api/{0}/sites/{1}/projects".format(Tools.VERSION, site_id)
    paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page_num)
    server_response = requests.get(paged_url, headers={'x-tableau-auth': auth_token})
    Tools.check_status(server_response, 200)
    xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))

    # Used to determine if more requests are required to find all projects on server
    total_projects = int(xml_response.find('t:pagination', namespaces=Tools.XMLNS).get('totalAvailable'))
    max_page = int(math.ceil(total_projects / page_size))

    projects = xml_response.findall('.//t:project', namespaces=Tools.XMLNS)

    # Continue querying if more projects exist on the server
    for page in range(2, max_page + 1):
        paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page)
        server_response = requests.get(paged_url, headers={'x-tableau-auth': auth_token})
        Tools.check_status(server_response, 200)
        xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
        projects.extend(xml_response.findall('.//t:project', namespaces=Tools.XMLNS))

    # Look through all projects to find the 'default' one
    for project in projects:
        if project.get('name') == project_name:  # .replace(" ", ""):
            return project.get('id')
    raise LookupError("Project was not found on server")


def file_extension_check(file_extension, filename, project_id, ds_user, ds_pass, embed):
    """
    Function to check the file extention to allow for the publish command to handle either workbooks or data sources
    :param file_extension:
    :param filename:
    :param project_id:
    :param ds_user:
    :param ds_pass:
    :param embed: Are the credentials Embedded, true/false
    :return: upload_content, upload_content_type, xml_request
    """
    if file_extension == 'twbx' or file_extension == 'twb':
        upload_content = "workbooks"
        upload_content_type = "workbookType"

        # Build a general request for publishing
        xml_request = ET.Element('tsRequest')
        workbook_element = ET.SubElement(xml_request, 'workbook', name=filename)
        ET.SubElement(workbook_element, 'project', id=project_id)
        xml_request = ET.tostring(xml_request)
    elif file_extension == 'tde' or file_extension == 'tbsx':
        if embed == "":
            embed = "false"
        upload_content = "datasources"
        upload_content_type = "datasourceType"

        # Build a general request for publishing
        xml_request = ET.Element('tsRequest')
        datasource_element = ET.SubElement(xml_request, 'datasource', name=filename)
        # errors as always creates elements in alphabetical order.
        ET.SubElement(datasource_element, 'connectionCredentials', name=ds_user, password=ds_pass, embed=embed)
        ET.SubElement(datasource_element, 'project', id=project_id)
        xml_request = ET.tostring(xml_request)
    else:
        # Call twb publish methods - long term
        error = "This is an unsupported file type."
        raise Tools.UserDefinedFieldError(error)
    print(xml_request)
    return upload_content, upload_content_type, xml_request


def publish(project, authentication, upload_file_path, parameter, ds_user="", ds_pass="", embed=""):
    """
     Handles the publishing of Tableau Workbooks and Tableau Datasources based on the file extension.
    :param project: string of project name.
    :param authentication: authentication object
    :param upload_file_path: File path including extension
    :param parameter: overwrite or (append if TDE)true or false
    :return:
    """
    ##### STEP 0: INITIALIZATION #####
    server = authentication.server
    username = authentication.username
    auth_token = authentication.get_token()
    site_id = authentication.get_site_id()

    # workbook_file_path = raw_input("\nWorkbook file to publish (include file extension): ")
    upload_file_path = os.path.abspath(upload_file_path)

    # Workbook file with extension, without full path
    upload_file = os.path.basename(upload_file_path)

    print("\n*Publishing '{0}' to the {1} project as {2}*".format(upload_file, project, username))

    if not os.path.isfile(upload_file_path):
        error = "{0}: file not found".format(upload_file_path)
        raise IOError(error)

    # Break workbook file by name and extension
    filename, file_extension = upload_file.split('.', 1)

    # Get workbook size to check if chunking is necessary
    size = os.path.getsize(upload_file_path)
    chunked = size >= FILESIZE_LIMIT

    ##### STEP 2: OBTAIN DEFAULT PROJECT ID #####
    print("\n2. Finding the '{0}' project to publish to)".format(project))
    project_id = get_project_id(server, project, auth_token, site_id)

    upload_content, upload_content_type, xml_request = file_extension_check(file_extension, filename, project_id,
                                                                            ds_user, ds_pass, embed)

    if chunked:
        print("\n3. Publishing '{0}' in {1}MB chunks (workbook over 64MB)".format(upload_file, CHUNK_SIZE / 1024000))
        # Initiates an upload session
        uploadID = start_upload_session(server, auth_token, site_id)

        # URL for PUT request to append chunks for publishing
        put_url = server + "/api/{0}/sites/{1}/fileUploads/{2}".format(Tools.VERSION, site_id, uploadID)

        # Read the contents of the file in chunks of 100KB
        with open(upload_file_path, 'rb') as f:
            while True:
                data = f.read(CHUNK_SIZE)
                if not data:
                    break
                payload, content_type = Tools.make_multipart({'request_payload': ('', '', 'text/xml'),
                                                              'tableau_file': (
                                                                  'file', data, 'application/octet-stream')})
                print("\tPublishing a chunk...")
                server_response = requests.put(put_url, data=payload,
                                               headers={'x-tableau-auth': auth_token, "content-type": content_type})
                Tools.check_status(server_response, 200)

        # Finish building request for chunking method
        payload, content_type = Tools.make_multipart({'request_payload': ('', xml_request, 'text/xml')})
        # workbooks || datasources
        publish_url = server + "/api/{0}/sites/{1}/{2}".format(Tools.VERSION, site_id, upload_content)
        publish_url += "?uploadSessionId={0}".format(uploadID)
        # workbookType || datasourceType
        if upload_content_type == "workbookType":
            publish_url += "&{0}={1}&overwrite={2}".format(upload_content_type, file_extension, parameter)
        elif upload_content_type == "datasourceType" and file_extension == 'tde':
            publish_url += "&{0}={1}&append={2}".format(upload_content_type, file_extension, parameter)
        else:
            publish_url += "&{0}={1}&overwrite={2}".format(upload_content_type, file_extension, parameter)
    else:
        print("\n3. Publishing '" + upload_file + "' using the all-in-one method (workbook under 64MB)")
        # Read the contents of the file to publish
        with open(upload_file_path, 'rb') as f:
            workbook_bytes = f.read()
        # Finish building request for all-in-one method
        parts = {'request_payload': ('', xml_request, 'text/xml'),
                 'tableau_workbook': (upload_file, workbook_bytes, 'application/octet-stream')}
        payload, content_type = Tools.make_multipart(parts)

        publish_url = server + "/api/{0}/sites/{1}/{2}?".format(Tools.VERSION, site_id, upload_content)
        if upload_content_type == "workbookType":
            publish_url += "&{0}={1}&overwrite={2}".format(upload_content_type, file_extension, parameter)
        elif upload_content_type == "datasourceType" and file_extension == 'tde':
            publish_url += "&{0}={1}&append={2}".format(upload_content_type, file_extension, parameter)
        else:
            publish_url += "&{0}={1}&overwrite={2}".format(upload_content_type, file_extension, parameter)
    # Make the request to publish and check status code
    print("\tUploading...")
    server_response = requests.post(publish_url, data=payload,
                                    headers={'x-tableau-auth': auth_token, 'content-type': content_type})
    Tools.check_status(server_response, 201)

    # ##### STEP 4: SIGN OUT #####
    # print("\n4. Signing out, and invalidating the authentication token")
    # authentication.sign_out()
