"""Firestore Class file."""

from google.cloud import firestore


class Firestore(object):
    """Firestore class."""

    def __init__(self, auth, github, project='broad-bitsdb-firestore'):
        """Initialize a class instance."""
        self.github = github
        self.project = project

        self.firestore = firestore
        self.db = firestore.Client(self.project)

        self.bitsdb_project = 'broad-bitsdb-prod'
        self.bitsdb = firestore.Client(self.bitsdb_project)

    def get_people(self):
        """Return a list of people."""
        fields = [
            'email_username',
            'emplid',
            'full_name',
            'github_id',
            'terminated',
        ]
        query = self.db.collection('people_people').select(fields)
        people = []
        for item in query.stream():
            people.append(item.to_dict())
        return people

    def get_people_dict(self, key='email_username'):
        """Return a dict of people by username."""
        people = {}
        for p in self.get_people():
            email = p[key]
            people[email] = p
        return people

    def get_team_syncs(self):
        """Return a list of team syncs."""
        query = self.bitsdb.collection('github_team_syncs')
        team_syncs = []
        for item in query.stream():
            team_syncs.append(item.to_dict())
        return team_syncs

    def get_team_syncs_dict(self, key='github_team_slug'):
        """Return a dict of team syncs by team id."""
        team_syncs = {}
        for s in self.get_team_syncs():
            team_id = s[key]
            team_syncs[team_id] = s
        return team_syncs
