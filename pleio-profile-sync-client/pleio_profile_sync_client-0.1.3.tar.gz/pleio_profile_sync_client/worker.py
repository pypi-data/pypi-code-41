import logging
import os
from requests.exceptions import HTTPError

logger = logging.getLogger(__name__)


# Worker reads from a queue and performs update and ban POST actions
class Worker:
    def __init__(self, queue, source, destination):
        self.queue = queue
        self.source = source
        self.destination = destination

    def run(self):
        while True:
            task, user = self.queue.get()

            if task == 'STOP':
                break

            logger.debug('[%s] guid:%s email:%s', task, user.get('guid'), user.get('email'))

            if task == 'UPDATE':
                self.update_user(user)
            elif task == 'BAN':
                self.ban_user(user)

    def update_user(self, user):
        if not (user.get('email') and user.get('name')):
            logger.error('Skipping user, required fields: [guid, email]')
            return False

        try:
            result = self.destination.post_user(user)
            if user.get('avatar') and result:
                avatar_path = os.path.join(os.path.dirname(self.source), user['avatar'])
                with open(avatar_path, 'rb') as avatar:
                    self.destination.post_avatar(result['user']['guid'], avatar)

                if user.get('guid'):
                    logger.debug('Updated user %s', result['user']['guid'])
                else:
                    logger.debug('Added user %s', result['user']['guid'])
        except HTTPError as e:
            logger.error('Error during adding / updating %s, %s, %s', user['email'], e, e.response.text)
        except FileNotFoundError as e:
            logger.error('Could not find avatar of %s', user['email'])

        return True

    def ban_user(self, user):
        try:
            self.destination.ban_user(user['guid'])
        except HTTPError as e:
            logger.error('Error during banning %s, %s, %s', user['email'], e, e.response.text)
