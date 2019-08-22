"""Datastore Class file."""

from google.cloud import datastore


class Datastore(object):
    """Datastore class."""

    def __init__(self, auth, github, project='broad-github'):
        """Initialize a class instance."""
        self.datastore = datastore
        self.github = github
        self.project = project

        self.db = datastore.Client(self.project)

    def list_entities(self, kind):
        """Return a list of all entities of a given kind."""
        query = self.db.query(kind=kind)
        return list(query.fetch())

    def list_entities_dict(self, kind):
        """Return a dict of all entities of a given kind."""
        entities = {}
        query = self.db.query(kind=kind)
        for entity in query.fetch():
            entity_key = entity.key.id
            if not entity_key:
                entity_key = entity.key.name
            entities[entity_key] = dict(entity)
        return entities

    def get_groups(self):
        """Return a list of groups from the GitHub app."""
        return self.list_entities('GoogleGroup')

    def get_groups_dict(self):
        """Return a list of groups from the GitHub app."""
        return self.list_entities_dict('GoogleGroup')

    def get_users(self):
        """Return a list of users from the GitHub app."""
        return self.list_entities('GitHubUser')

    def get_users_dict(self):
        """Return a list of users from the GitHub app."""
        return self.list_entities_dict('GitHubUser')
