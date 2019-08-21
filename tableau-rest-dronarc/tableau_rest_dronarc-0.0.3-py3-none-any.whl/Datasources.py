from tableau_rest import Tools
import requests  # Contains methods used to make HTTP requests
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML


class Datasource:
    def __init__(self, username, password, embed, oauth):
        self.username = username
        self.password = password
        self.embed = embed
        self.oauth = oauth

    def publish(self):
        pass

    def add_tags(self):
        pass

    def delete_tag(self):
        pass

    def query(self):
        pass

    def download(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass


class Datasource_Revision(Datasource):
    def get(self):
        pass

    def download(self):
        pass

    def remove(self):
        pass


class Datasource_Connection(Datasource):
    def query(self):
        pass

    def update(self):
        pass
