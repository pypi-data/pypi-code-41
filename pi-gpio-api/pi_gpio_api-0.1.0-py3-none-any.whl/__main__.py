import argparse
import daemonocle
from pi_gpio_api.core.app import app


def parse_args():
    parser = argparse.ArgumentParser('gpioapi',
                                     description="GPIO web API controller")

    parser.add_argument('command', metavar='command', type=str,
                        help='Control process: start, stop, restart, status',
                        choices=['start', 'stop', 'restart', 'status'])
    parser.add_argument('-H', '--host', default="0.0.0.0",
                        help='host where the web server will be listening')
    parser.add_argument('-p', '--port', default="5000",
                        help='port where the web server will be listening')
    return parser.parse_args()


def main():
    def cb_shutdown():
        print('Daemon is stopping')

    def main_loop():
        app.run(host=args.host, port=args.port)

    args = parse_args()
    daemon = daemonocle.Daemon(
        worker=main_loop,
        shutdown_callback=cb_shutdown,
        pidfile='/tmp/gpioapi.pid'
    )
    daemon.do_action(args.command)


if __name__ == '__main__':
    main()
