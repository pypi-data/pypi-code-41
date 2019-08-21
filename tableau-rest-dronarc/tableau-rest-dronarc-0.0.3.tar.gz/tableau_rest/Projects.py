from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import logging

logger = logging.getLogger()


def create(authentication, name, description, log):
    """
    Creates the Project on the server. However to store this project into a project obj you will need to query the
    server.
    :param authentication: authentication: <authentication obj> :class Auth:
    :param name: Project Name
    :param description: Project Description
    :param log: log: <logging obj>
    """
    logger = log
    url = authentication.server + "/api/{0}/sites/{1}/projects".format(Tools.VERSION, authentication.site_id)

    # xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
    xml_request = ET.Element('tsRequest')
    project_element = ET.SubElement(xml_request, 'project', parentProjectId="", name=name, description=description,
                                    contentPermissions="LockedToProject")
    xml_request = ET.tostring(xml_request)
    server_response = authentication.session.post(url, data=xml_request,
                                                  headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 201)


def query(authentication, log, name=""):
    """
    Returns Project(s) from Tableau Server.
    :param authentication: <authentication obj> :class Auth:
    :param log: <logging obj>
    :param name: if not stated will return all projects on specified server.
    :return:
    """
    logger = log
    done = False
    page_size = 100
    page_number = 1
    total_returned = 0

    output_projects = []

    if name == "":
        logger.debug("No name specified, pulling all projects")

    while not (done):
        url = authentication.server + "/api/{0}/sites/{1}/projects".format(Tools.VERSION,
                                                                           authentication.site_id)
        url += "?pageSize={0}&pageNumber={1}".format(page_size, page_number)

        server_response = authentication.session.get(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
        # Get total number of records from the <pagination> element
        total_available = xml_response.find('.//t:pagination',
                                            namespaces={'t': "http://tableau.com/api"}).attrib['totalAvailable']
        # Note! Need to convert "total_available" to integer
        total_available = int(total_available)

        page_number += 1
        total_returned += page_size
        projects = xml_response.findall('.//t:project', namespaces=Tools.XMLNS)

        for p in projects:
            if name == "":
                project = Project(p.get('id'), p.get('name'), p.get('description'),
                                  p.get('contentPermission'))
                output_projects.append(project)
            elif p.get('name') == name:
                project = Project(p.get('id'), p.get('name'), p.get('description'),
                                  p.get('contentPermission'))
                return project
        if total_returned >= total_available:
            done = True
            if name == "":
                return output_projects
    error = "Project named '{0}' not found.".format(name)
    raise LookupError(error)


class Project:
    """Project handler for Tableau's Rest API. Creates a Project object which holds all functions related
     to specific Project."""

    def __init__(self, project_id, name, description, content_permissions):
        """
        Creates the Project object storing the appropriate info. Requires project_id which can only be pulled from the
        Tabelau server. So users must be logged in and object created from the :func query:
        :param project_id:
        :param name:
        :param description:
        :param content_permissions:
        """
        self.project_id = project_id
        self.name = name
        self.description = description
        self.content_permissions = content_permissions

    def add_tags(self):
        pass

    def update(self, authentication, name="", description="", owners=[], limit="", lifecycle=""):
        """
        Use to change details of the current Project Object on the Server. Will take current values if new value not
        specified.
        :param authentication:
        :param name:
        :param description:
        :param owners:
        :param limit:
        :param lifecycle:
        :return:
        """
        approvers = ""
        count = 0

        if name == "":
            name = self.name

        if not len(owners) < 1:
            for owner in owners:
                if not count > 3:
                    if count == 0:
                        approvers += "<approver>" + owner + "</approver>"
                        count += 1
                    else:
                        approvers += ", " + "<approver" + str(count) + ">" + owner + "</approver" + str(count) + ">"
                        count += 1

        if description == "":
            description = self.description
            # "\n\nThe project owner(s) and approver(s) for this project is " + approvers \
            description += ".\n\nThis project will have a user limit of " + " <userlimit>" + str(
                limit) + "</userlimit> users."
            # users across it's lifecycle of <projectlife>" + lifecycle + "</projectlife>."

        url = authentication.server + "/api/{0}/sites/{1}/projects/{2}".format(Tools.VERSION, authentication.site_id,
                                                                               self.project_id)

        # xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))
        xml_request = ET.Element('tsRequest')
        project_element = ET.SubElement(xml_request, 'project', parentProjectId="", name=name, description=description,
                                        contentPermissions="LockedToProject")
        xml_request = ET.tostring(xml_request)

        server_response = authentication.session.put(url, data=xml_request,
                                                     headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)

    def delete(self, authentication):
        url = authentication.server + "/api/{0}/sites/{1}/projects/{2}".format(Tools.VERSION, authentication.site_id,
                                                                               self.project_id)

        server_response = authentication.session.delete(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 204)
