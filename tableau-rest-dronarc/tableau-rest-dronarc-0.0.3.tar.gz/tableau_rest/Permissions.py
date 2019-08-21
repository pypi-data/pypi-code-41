from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML


def add(authentication, level, capability, project_id, group_user, group_id):
    '''
    Function to add default permissions at a project level
    :param authentication: The authentication object holding all information for the signed in session
    :param level: "project", "workbooks", "datasources" specifying what level of permissions to add.
    :param capability: Key value pair, consisting of below permissions followed by "Allow"/"Deny"
    projects: ProjectLeader, Read, Write
    workbooks : AddComment, ChangeHierarchy, ChangePermissions, Delete, ExportData, ExportImage, ExportXml,
    Filter, Read, ShareView, ViewComments, ViewUnderlyingData, WebAuthoring, and Write.
    datasources : ChangePermissions, Connect, Delete, ExportXml, Read (view), and Write.
    :param project_id: id for the project that you are assigning the permissions
    :param group_user: String to specify group or user
    :param group_id: id of the group receiving the permissions, interchangable with user id
    :return:
    '''
    level = level.lower()
    if level == "project":
        url = authentication.server + "/api/{0}/sites/{1}/projects/{2}/permissions".format(Tools.VERSION,
                                                                                           authentication.site_id,
                                                                                           project_id)
    else:
        url = authentication.server + "/api/{0}/sites/{1}/projects/{2}/default-permissions/{3}".format(Tools.VERSION,
                                                                                                       authentication.site_id,
                                                                                                       project_id,
                                                                                                       level)

    xml_request = ET.Element('tsRequest')
    project_element = ET.SubElement(xml_request, 'permissions')
    capability_element = ET.SubElement(project_element, "granteeCapabilities")
    group_element = ET.SubElement(capability_element, group_user, id=group_id)
    capabilities = ET.SubElement(capability_element, "capabilities")
    for key, value in capability.items():
        ET.SubElement(capabilities, "capability", name=key, mode=value)
    xml_request = ET.tostring(xml_request)

    server_response = authentication.session.put(url, data=xml_request, headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 200)


def add_workbook(authentication, capability, workbook_id, group_user, group_id):
    '''
    Function to add permissions at a workbook level
    :param authentication: The authentication object holding all information for the signed in session
    :param capability: Key value pair, consisting of below permissions followed by "Allow"/"Deny"
    AddComment, ChangeHierarchy, ChangePermissions, Delete, ExportData, ExportImage, ExportXml,
    Filter, Read, ShareView, ViewComments, ViewUnderlyingData, WebAuthoring, and Write.
    :param workbook_id: id for the project that you are assigning the permissions
    :param group_user: String to specify group or user
    :param group_id: id of the group receiving the permissions, interchangable with user id
    :return:
    '''
    url = authentication.server + "/api/{0}/sites/{1}/workbooks/{2}/permissions".format(Tools.VERSION,
                                                                                        authentication.site_id,
                                                                                        workbook_id)
    xml_request = ET.Element('tsRequest')
    project_element = ET.SubElement(xml_request, 'permissions')
    ET.SubElement(xml_request, "workbook", id=workbook_id)
    capability_element = ET.SubElement(project_element, "granteeCapabilities")
    group_element = ET.SubElement(capability_element, group_user, id=group_id)
    capabilities = ET.SubElement(capability_element, "capabilities")
    for key, value in capability.items():
        ET.SubElement(capabilities, "capability", name=key, mode=value)
    xml_request = ET.tostring(xml_request)

    server_response = authentication.session.put(url, data=xml_request, headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 200)


def add_datasource(authentication, capability, datasource_id, group_user, group_id):
    '''
    Function to add default permissions at a datasources level
    :param authentication: The authentication object holding all information for the signed in session
    :param capability: Key value pair, consisting of below permissions followed by "Allow"/"Deny"
    AddComment, ChangeHierarchy, ChangePermissions, Delete, ExportData, ExportImage, ExportXml,
    Filter, Read, ShareView, ViewComments, ViewUnderlyingData, WebAuthoring, and Write.
    :param project_id: id for the project that you are assigning the permissions
    :param group_user: String to specify group or user
    :param group_id: id of the group receiving the permissions, interchangable with user id
    :return:
    '''
    url = authentication.server + "/api/{0}/sites/{1}/datasources/{2}/permissions".format(Tools.VERSION,
                                                                                          authentication.site_id,
                                                                                          datasource_id)
    xml_request = ET.Element('tsRequest')
    project_element = ET.SubElement(xml_request, 'permissions')
    ET.SubElement(xml_request, "datasource", id=datasource_id)
    capability_element = ET.SubElement(project_element, "granteeCapabilities")
    group_element = ET.SubElement(capability_element, group_user, id=group_id)
    capabilities = ET.SubElement(capability_element, "capabilities")
    for key, value in capability.items():
        ET.SubElement(capabilities, "capability", name=key, mode=value)
    xml_request = ET.tostring(xml_request)

    server_response = authentication.session.put(url, data=xml_request, headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 200)
