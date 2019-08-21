from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import os
import re
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import logging
from datetime import datetime

logger = logging.getLogger()


def query(authentication, log, name="", project_id=""):
    """
    Gets the workbook info and stores it
    :param authentication: authentication object that grants user access to API calls and holds any signin info
    :param name: the name of the workbook
    :return:
    """
    done = False
    page_size = 100
    page_number = 1
    total_returned = 0
    logger = log
    output_twbs = []

    if name == "":
        logger.debug("No name specified, pulling all workbooks")

    while not (done):
        # try:
        url = authentication.server + "/api/{0}/sites/{1}/workbooks".format(Tools.VERSION,
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
        workbooks = xml_response.findall('.//t:workbook', namespaces=Tools.XMLNS)

        for w in workbooks:
            if name == "":
                if project_id == "":
                    source_project_id = w.find('.//t:project', namespaces=Tools.XMLNS).get('id')

                    workbook = Workbook(w.get('name'), w.get('id'), w.get('contentUrl'), w.get('createdAt'),
                                        w.get('updatedAt'), source_project_id)
                    output_twbs.append(workbook)
                else:
                    if w.find('.//t:project', namespaces=Tools.XMLNS).get('id') == project_id:
                        logger.debug("Match found for given project_id")
                        source_project_id = w.find('.//t:project', namespaces=Tools.XMLNS).get('id')

                        workbook = Workbook(w.get('name'), w.get('id'), w.get('contentUrl'), w.get('createdAt'),
                                            w.get('updatedAt'), 'source_project_id)')
                        output_twbs.append(workbook)
                    else:
                        continue

            elif w.get('name') == name:
                source_project_id = w.find('.//t:project', namespaces=Tools.XMLNS).get('id')

                workbook = Workbook(w.get('name'), w.get('id'), w.get('contentUrl'), w.get('createdAt'),
                                    w.get('updatedAt'), source_project_id)
                return workbook

        if total_returned >= total_available:
            done = True
            if name == "":
                return output_twbs

    error = "Workbook named '{0}' not found.".format(name)
    raise LookupError(error)
    # except LookupError:
    #   print(error)


def download(packaged, authentication, workbook_id, path):
    if packaged:
        url = authentication.server + "/api/{0}/sites/{1}/workbooks/{2}/content?includeExtract=True".format(
            Tools.VERSION,
            authentication.site_id,
            workbook_id)
    else:
        url = authentication.server + "/api/{0}/sites/{1}/workbooks/{2}/content?includeExtract=False".format(
            Tools.VERSION,
            authentication.site_id,
            workbook_id)
    server_response = authentication.session.get(url, headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 200)
    # Header format: Content-Disposition: name="tableau_workbook"; filename="workbook-filename"
    # filename = re.findall(r'filename="(.*)"', server_response.headers['Content-Disposition'])[0]
    extension = re.findall(r'filename="(.*)"', server_response.headers['Content-Disposition'])[0]
    extension = extension.split('.')[1]
    with open("{}.{}".format(path, extension), 'wb') as f:
        f.write(server_response.content)
        return "{}.{}".format(path, extension)


def query_view(authentication, name, workbook_id):
    """
    Gets the workbook info and stores it
    :param authentication: authentication object that grants user access to API calls and holds any signin info
    :param name: the name of the workbook
    :return:
    """
    url = authentication.server + "/api/{0}/sites/{1}/workbooks/{2}/views?includeUsageStatistics=true".format(
        Tools.VERSION,
        authentication.site_id,
        workbook_id)

    server_response = authentication.session.get(url, headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 200)
    xml_response = ET.fromstring(Tools.encode_for_display(server_response.text))

    views = xml_response.findall('.//t:view', namespaces=Tools.XMLNS)

    for v in views:
        if v.get('name') == name:
            # source_workbook_id = v.find('.//t:workbook', namespaces=Tools.XMLNS).get('id')
            # source_owner_id = v.find('.//t:owner', namespaces=Tools.XMLNS).get('id')
            # source_view_count = v.find('.//t:usage', namespaces=Tools.XMLNS).get('totalViewCount')

            view = View(v.get('name'), v.get('id'), v.get('contentUrl'), workbook_id)
            # source_owner_id, source_view_count)
            return view
    error = "View named '{0}' not found.".format(name)
    raise LookupError(error)


class Workbook:
    """ Workbook handler for Tableau's Rest API. Creates a Workbook object which holds all functions related to specific
    Workbook.
    """

    def __init__(self, name, workbook_id, url, createdAt, updatedAt, project_id):
        """
        Creates the Workbook object storing the appropriate info. Requires workbook_id which can only be pulled from the
        Tabelau server. So users must be logged in and object created from the :func query:
        :param name:
        :param workbook_id:
        :param url:
        :param project_id:
        """
        self.name = name
        self.workbook_id = workbook_id
        self.url = url

        date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.createdAt = datetime.strptime(createdAt, date_format)
        self.updatedAt = datetime.strptime(updatedAt, date_format)
        self.project_id = project_id
        self.project_name = ""
        self.lastViewed = ""
        self.tags = ""
        self.views = ""

    def set_project_name(self, project_name):
        """Set Project Name"""
        self.project_name = project_name

    def set_lastViewed(self, lastViewed):
        """Set Last Viewed"""
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        self.lastViewed = datetime.strptime(lastViewed, date_format)

    def delete(self, authentication):
        url = authentication.server + "/api/{0}/sites/{1}/workbooks/{2}".format(Tools.VERSION, authentication.site_id,
                                                                                self.workbook_id)

        server_response = authentication.session.delete(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 204)


class View:
    """
    View handler for Tableau's Rest API. Creates a View object which holds all functions related
     to specific View.
    """

    def __init__(self, name, view_id, url, workbook_id):  # , owner_id, view_count):
        """Creates the View object storing the appropriate info. Requires view_id which can only be pulled from the
        Tabelau server. So users must be logged in and object created from the :func query_view:"""
        self.name = name
        self.view_id = view_id
        self.url = url
        self.workbook_id = workbook_id
        # self.owner_id = owner_id
        # self.view_count = view_count

    def download(self, authentication, export_type, path, filename, filters=""):
        filter_string = ""
        if export_type == "image":
            filename += ".png"
        if export_type == "data":
            filename += ".csv"
        if export_type == "PDF":
            # export_type = "image"
            filename += ".pdf"
        if not filters == "":
            filter_string = "?vf_" + filters
        url = authentication.server + "/api/{0}/sites/{1}/views/{2}/{3}{4}".format(
            Tools.VERSION,
            authentication.site_id, self.view_id, export_type, filter_string)

        server_response = authentication.session.get(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        # Header format: Content-Disposition: name="tableau_workbook"; filename="workbook-filename"
        # filename = re.findall(r'filename="(.*)"', server_response.headers['Content-Disposition'])[0]
        output = path + filename.replace('/', '-')
        with open(output, 'wb') as f:
            f.write(server_response.content)

    def get_preview_image(self, authentication, path, filename):
        url = authentication.server + "/api/{0}/sites/{1}/workbooks/{2}/views/{3}/previewImage".format(
            Tools.VERSION,
            authentication.site_id, self.workbook_id, self.view_id)

        server_response = authentication.session.get(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        # Header format: Content-Disposition: name="tableau_workbook"; filename="workbook-filename"
        # filename = re.findall(r'filename="(.*)"', server_response.headers['Content-Disposition'])[0]
        output = path + filename.replace('/', '-')
        with open(output, 'wb') as f:
            f.write(server_response.content)
