import logging
from .dict_reader import UserDictReader

logger = logging.getLogger(__name__)


# Mapper retrieves a list of source and destination users, maps them on external_id or email and determines which users
# to update and ban.
class Mapper:
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

        self.on_source = {'email': dict(), 'external_id': dict()}
        self.on_destination = {'email': dict(), 'external_id': dict()}

    def initialize(self):
        with open(self.source) as file_source:
            csv_source = UserDictReader(file_source)

            logger.info('Retrieving list of source users')
            for i, user in enumerate(csv_source):
                self.on_source['email'][user['email']] = i

                if user['external_id']:
                    self.on_source['external_id'][user['external_id']] = i

            logger.info('Retrieving list of destination users')
            for user in self.destination.get_users():
                self.on_destination['email'][user['email']] = user['guid']

                if user['external_id']:
                    self.on_destination['external_id'][user['external_id']] = user['guid']

    def users_to_update(self):
        with open(self.source) as file_source:
            csv_source = UserDictReader(file_source)
            for user in csv_source:
                guid = None

                if user['external_id'] in self.on_destination['external_id'].keys():
                    guid = self.on_destination['external_id'][user['external_id']]
                else:
                    if user['email'] in self.on_destination['email'].keys():
                        guid = self.on_destination['email'][user['email']]

                if guid:
                    yield({**user, 'guid': guid})
                else:
                    yield(user)

    def users_to_ban(self):
        for user in self.destination.get_users():
            if user['external_id'] in self.on_source['external_id']:
                continue

            if user['email'] in self.on_source['email']:
                continue

            yield user

    def count(self):
        return {
            'source': len(self.on_source['email'].keys()),
            'destination':  len(self.on_destination['email'].keys())
        }
