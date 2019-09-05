#!python

import argparse
import asterisk.manager
import nagiosplugin


class AsteriskSiptrunkContext(nagiosplugin.Context):

    def __init__(self):
        super(AsteriskSiptrunkContext, self).__init__('asterisksiptrunk')

    def evaluate(self, metric, resource):
        if 'OK' in metric.value:
            return self.result_cls(nagiosplugin.state.Ok, metric=metric, hint=metric.name + ' is ' + metric.value)
        else:
            return self.result_cls(nagiosplugin.state.Critical, metric=metric, hint=metric.name + ' is ' + metric.value)


class AsteriskSiptrunk(nagiosplugin.Resource):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.password = kwargs.pop('password')
        self.peer = kwargs.pop('peer')
        self.host = kwargs.pop('host')
        self.port = kwargs.pop('port')
        super(nagiosplugin.Resource, self).__init__(*args, **kwargs)

    def probe(self):
        manager = asterisk.manager.Manager()
        try:
        # connect to the manager
            try:
                manager.connect(self.host)
                manager.login(self.user, self.password)
                response = manager.sipshowpeer(self.peer)
                if response.headers.get('Response') != 'Success':
                    raise nagiosplugin.CheckError(response.headers.get('Message'))
                else:
                    status = response.headers.get('Status')
                    yield nagiosplugin.Metric(self.peer, status, context='asterisksiptrunk')
            except asterisk.manager.ManagerSocketException as e:
                raise nagiosplugin.CheckError(e)
            except asterisk.manager.ManagerAuthException as e:
                raise nagiosplugin.CheckError(e)
            except asterisk.manager.ManagerException as e:
                raise nagiosplugin.CheckError(e)

        finally:
            # remember to clean up
            manager.close()


@nagiosplugin.guarded
def main():
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-v', '--verbose', action='count', default=0, help='Increase output verbosity (use up to 3 times)')
    argp.add_argument('-H', '--host', default='127.0.0.1', help='IP Address for AMI')
    argp.add_argument('-P', '--port', default='5038', help='Port for AMI')
    argp.add_argument('user', help='Username for AMI')
    argp.add_argument('password', help='Password for AMI')
    argp.add_argument('peer', help='Name of the SIP peer to check')
    args = argp.parse_args()

    check = nagiosplugin.Check(
        AsteriskSiptrunk(user=args.user,
                         password=args.password,
                         peer=args.peer,
                         host=args.host,
                         port=args.port),
        AsteriskSiptrunkContext())
    check.main(args.verbose)


if __name__ == '__main__':
    main()
