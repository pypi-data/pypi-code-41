import sys

from cliff.command import Command

from peertube_uploader.utils import RelativeSession


# noinspection PyAbstractClass
class PeertubeBaseCommand(Command):
    """

    :type s: RelativeSession
    :type client_id: basestring
    :type client_secret: basestring
    """

    def __init__(self, app, app_args):
        """

        :param app:
        :type app:  cliff.app.App
        :param app_args:
        :type app_args: argparse.Namespace
        """
        super().__init__(app, app_args)
        self.s = None
        self.client_id = None
        self.client_secret = None

    def take_action(self, parsed_args):
        self.s = RelativeSession(self.app_args.endpoint)
        self.client_id = self.app_args.client_id
        self.client_secret = self.app_args.client_secret
        if not (self.client_id or self.client_secret):
            local__json = self.s.get("/api/v1/oauth-clients/local").json()
            self.client_id = local__json["client_id"]
            self.client_secret = local__json["client_secret"]
            self.app.LOG.info("""Please reuse these credentials
        client-id:{client_id}
        client-secret:{client_secret}
        """.format(client_id=self.client_id, client_secret=self.client_secret))

        if not self.app_args.access_token:
            auth_data = {'client_id': self.client_id,
                         'client_secret': self.client_secret,
                         'grant_type': 'password',
                         'response_type': 'code',
                         'username': self.app_args.username,
                         'password': self.app_args.password
                         }

            auth_result = self.s.post('/api/v1/users/token', data=auth_data)
            try:
                access_token = (auth_result.json()['access_token'])
            except:
                self.app.LOG.error(auth_result.text)
                sys.exit(1)
        else:
            access_token = self.app_args.access_token

        self.s.headers.update({'Authorization': 'Bearer {0}'.format(access_token)})
