from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import logging
from datetime import datetime

logger = logging.getLogger()


def query_group(authentication, log, name=''):
    """
    Returns group(s) from Tableau Server.
    :param authentication: <authentication obj> :class Auth:
    :param log: <logging obj>
    :param name: if not stated will return all groups on specified server.
    :return: <Group Obj> or list<Group Obj>
    """

    logger = log
    done = False
    page_size = 100
    page_number = 1
    total_returned = 0
    returned_groups = []
    while not (done):
        url = authentication.server + "/api/{0}/sites/{1}/groups".format(Tools.VERSION,
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
        groups = xml_response.findall('.//t:group', namespaces=Tools.XMLNS)
        for g in groups:
            if name == '':
                domain_name = g.find('.//t:domain', namespaces=Tools.XMLNS).get('name')
                group = Group(g.get('id'), g.get('name'), domain_name, logger)
                returned_groups.append(group)
            elif g.get('name') == name:
                domain_name = g.find('.//t:domain', namespaces=Tools.XMLNS).get('name')
                group = Group(g.get('id'), g.get('name'), domain_name, logger)
                return group
        if total_returned >= total_available:
            done = True

    if name == "":
        return returned_groups
    error = "Group named '{0}' not found.".format(name)
    raise LookupError(error)


def create_group(authentication, name, log):
    """
    Creates the Group on the server. However to store this group into a group obj you will need to query the
    server.
    :param authentication: authentication: <authentication obj> :class Auth:
    :param name: Group Name
    :param log: <logging obj>
    """
    logger = log
    url = authentication.server + "/api/{0}/sites/{1}/groups".format(Tools.VERSION, authentication.site_id)

    xml_request = ET.Element('tsRequest')
    group_element = ET.SubElement(xml_request, 'group', name=name)
    xml_request = ET.tostring(xml_request)
    server_response = authentication.session.post(url, data=xml_request,
                                                  headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 201)

    return Group("", name, "", logger)


def update_user(authentication, user, log):
    """
    Use to change details of the given User Object on the Server. Will take current values if new value not
    specified
    :param authentication: authentication: <authentication obj> :class Auth:
    :param user: Updated user object.
    :param log: <logging obj>
    :return:
    """
    # PUT /api/api-version/sites/site-id/users/user-id
    logger = log
    url = authentication.server + "/api/{0}/sites/{1}/users/{2}".format(Tools.VERSION, authentication.site_id,
                                                                        user.user_id)
    xml_request = ET.Element('tsRequest')
    # Currently we can only change site role, as everything else is drawn through AD
    user_element = ET.SubElement(xml_request, 'user', siteRole=user.site_role)
    xml_request = ET.tostring(xml_request)

    server_response = authentication.session.put(url, data=xml_request,
                                                 headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 200)


def add_to_site(authentication, name, site_role, log):
    logger = log
    url = authentication.server + "/api/{0}/sites/{1}/users".format(Tools.VERSION, authentication.site_id)
    xml_request = ET.Element('tsRequest')
    user_element = ET.SubElement(xml_request, 'user', name=name, siteRole=site_role)
    xml_request = ET.tostring(xml_request)

    server_response = authentication.session.post(url, data=xml_request,
                                                  headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 201)


def get_in_site():
    pass


def query_user(authentication, log, name=""):
    """
    Returns users(s) from Tableau Server.
    :param authentication: <authentication obj> :class Auth:
    :param log: <logging obj>
    :param name: if not stated will return all users on specified server.
    :return: <User Obj> or list<User Obj>
    """

    logger = log
    done = False
    page_size = 100
    page_number = 1
    total_returned = 0
    return_users = []
    while not (done):
        url = authentication.server + "/api/{0}/sites/{1}/users".format(Tools.VERSION,
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
        users = xml_response.findall('.//t:user', namespaces=Tools.XMLNS)

        for u in users:
            if name != "":
                if u.get('name').upper() == name.upper():
                    user = User(u.get('id'), u.get('name'), u.get('siteRole'), u.get('lastLogin'))
                    return user
            else:
                user = User(u.get('id'), u.get('name'), u.get('siteRole'), u.get('lastLogin'))
                return_users.append(user)
        if total_returned >= total_available:
            done = True
            if name == "":
                return return_users
    error = "User named '{0}' not found.".format(name)
    raise LookupError(error)


def remove_from_group():
    pass


def remove_from_site(authentication, user_id, logger):
    url = authentication.server + "/api/{0}/sites/{1}/users/{2}".format(Tools.VERSION, authentication.site_id,
                                                                        user_id)

    server_response = authentication.session.delete(url, headers={'x-tableau-auth': authentication.get_token()})
    Tools.check_status(server_response, 204)
    pass


class User:
    """
    User handler for Tableau's Rest API. Creates a User object which holds all functions related to specific User
    """

    def __init__(self, user_id, name, site_role, last_login):
        """
        Creates the User object storing the appropriate info. Requires user_id which can only be pulled from the
        Tableau server. So users must be logged in and object created from the :func query_user:
        :param user_id:
        :param name:
        :param site_role:
        :param last_login:
        """
        self.user_id = user_id
        self.name = name
        self.site_role = site_role
        date_format = "%Y-%m-%dT%H:%M:%SZ"
        try:
            self.last_login = datetime.strptime(last_login, date_format)
        except Exception as e:
            logger.warning("{}, User has never logged in. Therefore setting last login to blank.".format(e))
            self.last_login = last_login


class Group:
    """
    Group handler for Tableau's Rest API. Creates a Group object which holds all functions related to specific Group
    """

    def __init__(self, group_id, name, domain_name, log):
        """
        Creates the Group object storing the appropriate info. Requires group_id which can only be pulled from the
        Tableau server. So users must be logged in and object created from the :func query_group:
        :param group_id:
        :param name:
        :param domain_name:
        :param log:
        """
        self.group_id = group_id
        self.name = name
        self.domain_name = domain_name
        logger = log

    def get_details(self, authentication):
        done = False
        page_size = 100
        page_number = 1
        total_returned = 0

        while not (done):
            url = authentication.server + "/api/{0}/sites/{1}/groups".format(Tools.VERSION,
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
            groups = xml_response.findall('.//t:group', namespaces=Tools.XMLNS)

            for g in groups:
                if g.get('name') == self.name:
                    self.group_id = g.get('id')
                    if self.domain_name == "":
                        self.domain_name = g.find('.//t:domain', namespaces=Tools.XMLNS).get('name')
                    return self
            if total_returned >= total_available:
                done = True
        error = "Group named '{0}' not found.".format(self.name)
        raise LookupError(error)

    def get_users(self, authentication):
        done = False
        page_size = 100
        page_number = 1
        total_returned = 0
        users_in_group = []

        while not (done):
            url = authentication.server + "/api/{0}/sites/{1}/groups/{2}/users".format(Tools.VERSION,
                                                                                       authentication.site_id,
                                                                                       self.group_id)
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
            users = xml_response.findall('.//t:user', namespaces=Tools.XMLNS)
            for u in users:
                user = User(u.get('id'), u.get('name'), u.get('siteRole'), u.get('lastLogin'))
                users_in_group.append(user)
            if total_returned >= total_available:
                done = True
        return users_in_group

    def query_in_group(self):
        pass

    def update(self):
        pass

    def delete(self, authentication):
        url = authentication.server + "/api/{0}/sites/{1}/groups/{2}".format(Tools.VERSION, authentication.site_id,
                                                                             self.group_id)

        server_response = authentication.session.delete(url, headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 204)

    def add(self, authentication, user_id):
        """
        Adds the given user_id to the current group.
        :param authentication:
        :param user_id:
        :return:
        """
        url = authentication.server + "/api/{0}/sites/{1}/groups/{2}/users".format(Tools.VERSION,
                                                                                   authentication.site_id,
                                                                                   self.group_id)

        xml_request = ET.Element('tsRequest')
        # for user_id in user_ids:
        group_element = ET.SubElement(xml_request, 'user', id=user_id)

        xml_request = ET.tostring(xml_request)

        server_response = authentication.session.post(url, data=xml_request,
                                                      headers={'x-tableau-auth': authentication.get_token()})
        Tools.check_status(server_response, 200)
        # print(server_response.text)
