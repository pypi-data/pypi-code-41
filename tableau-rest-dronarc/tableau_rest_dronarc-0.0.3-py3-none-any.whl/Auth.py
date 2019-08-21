from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML
import os
import logging

logger = logging.getLogger()


class Auth:
    """Authentication handler for Tableau's Rest API. Creates a authentication object which holds all functions related
     to authentication. Instance will timeout after approx. 4 hours, will need to sign back in to update token."""

    def __init__(self, server, site, username, password, log, path_to_cert=""):
        """Authentication's init function builds all the information for the object.
        :param server: <string> Takes a server URL, we currently hardcode the certs based off of this.
        :param site: <string> Blank for default site otherwise must be case sensitive.
        :param username: <string> user account on tableau server. Please only use real users not generic accounts.
        :param password: <string> password is not encrypted during run in current iteration.
        :param log: <logging Obj> the log file to out put information.
        :return auth: object for handling any authentication calls. Sign in stores access token for approx 4hrs.
        :rtype: <Auth Obj>
        """
        self.server = server
        self.site = site
        self.username = username
        self.password = password
        self.site_id = ""
        self.user_id = ""
        self.token = ""
        self.viz_token = ""
        self.session = requests.Session()
        if not path_to_cert == "":
            self.session.verify = path_to_cert
        logger = log

    def sign_in(self):
        """Sign into tableau Server, creating the Authentication Token and other IDs which are only available from a
         signed in user"""
        url = self.server + "/api/{0}/auth/signin".format(Tools.VERSION)
        # Builds the request
        xml_payload = ET.Element('tsRequest')
        credentials_element = ET.SubElement(xml_payload, 'credentials', name=self.username, password=self.password)
        ET.SubElement(credentials_element, 'site', contentUrl=self.site)
        xml_payload = ET.tostring(xml_payload)
        logger.info("Signing in as {}, to {} on the {} site...".format(self.username, self.server, self.site))
        # Make the request to server
        server_response = self.session.post(url, data=xml_payload)
        Tools.check_status(server_response, 200)

        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)
        # Reads and parses the response
        parsed_response = ET.fromstring(server_response)
        logger.debug("Returned a response of {}".format(parsed_response))

        # Gets the auth token, site ID and user ID
        self.set_token(parsed_response.find('t:credentials', namespaces=Tools.XMLNS).get('token'))
        self.set_site_id(parsed_response.find('.//t:site', namespaces=Tools.XMLNS).get('id'))
        self.set_user_id(parsed_response.find('.//t:user', namespaces=Tools.XMLNS).get('id'))
        logger.info("Signed in as {}, to {} on the {} site...".format(self.username, self.server, self.site))

        return self.get_token

    def sign_in_as(self, user_id):
        """Sign into tableau Server as a user. If user is not unique it will require domain. Creating the Authentication
         Token"""
        url = self.server + "/api/{0}/auth/signin".format(Tools.VERSION)
        # Builds the request
        xml_payload = ET.Element('tsRequest')
        credentials_element = ET.SubElement(xml_payload, 'credentials', name=self.username, password=self.password)
        ET.SubElement(credentials_element, 'site', contentUrl=self.site)
        ET.SubElement(credentials_element, 'user', id=user_id)
        xml_payload = ET.tostring(xml_payload)
        logger.info("\nSigning in as {}, to {} on the {} site...".format(self.username, self.server, self.site))
        # Make the request to server
        server_response = self.session.post(url, data=xml_payload)
        Tools.check_status(server_response, 200)

        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

        # Reads and parses the response
        parsed_response = ET.fromstring(server_response)
        logger.debug("Returned a response of {}".format(parsed_response))

        # Gets the auth token, site ID and user ID of the signed in user.
        self.set_token(parsed_response.find('t:credentials', namespaces=Tools.XMLNS).get('token'))
        self.set_site_id(parsed_response.find('.//t:site', namespaces=Tools.XMLNS).get('id'))
        self.set_user_id(parsed_response.find('.//t:user', namespaces=Tools.XMLNS).get('id'))
        logger.info("\nSigned in as {}, to {} on the {} site...".format(self.username, self.server, self.site))

        return self.get_token

    def sign_out(self):
        """Sign out of tableau Server, destroying the Authentication Token"""
        url = self.server + "/api/{0}/auth/signout".format(Tools.VERSION)
        server_response = self.session.post(url, headers={'x-tableau-auth': self.token})
        Tools.check_status(server_response, 204)
        self.set_token("")
        del self
        return

    def swap_site(self, site):
        url = self.server + "/api/{0}/auth/switchSite".format(Tools.VERSION)

        if site == "":
            site_name = "Default Site"
        else:
            site_name = site

        # Builds the request
        xml_payload = ET.Element('tsRequest')
        credentials_element = ET.SubElement(xml_payload, 'site', contentUrl=site.replace(" ", ""))
        xml_payload = ET.tostring(xml_payload)
        print("\nSwapping site to", site_name, "...")
        # Make the request to server
        server_response = self.session.post(url, headers={'x-tableau-auth': self.get_token()}, data=xml_payload)
        Tools.check_status(server_response, 200)

        # ASCII encode server response to enable displaying to console
        server_response = Tools.encode_for_display(server_response.text)

        # Reads and parses the response
        parsed_response = ET.fromstring(server_response)

        # Gets the auth token, site ID and user ID
        self.set_token(parsed_response.find('t:credentials', namespaces=Tools.XMLNS).get('token'))
        self.set_site_id(parsed_response.find('.//t:site', namespaces=Tools.XMLNS).get('id'))
        self.set_user_id(parsed_response.find('.//t:user', namespaces=Tools.XMLNS).get('id'))
        print("\nNow Signed into", site_name)

        return self.get_token

    def __del__(self):
        logger.debug("{} deleted".format(self))

    def get_token(self):
        """Return Authentication Token"""
        return self.token

    def set_token(self, token):
        """Set Authentication Token"""
        self.token = token

    def get_site_id(self):
        """Return site id"""
        return self.site_id

    def set_site_id(self, site_id):
        """Set site id"""
        self.site_id = site_id

    def get_user_id(self):
        """Return user id"""
        return self.user_id

    def set_user_id(self, user_id):
        """Set user id"""
        self.user_id = user_id

    def get_viz_token(self):
        """Return user id"""
        return self.viz_token

    def set_viz_token(self, viz_token):
        """Set user id"""
        self.viz_token = viz_token
