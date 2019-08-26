import argparse
import urllib.request
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scheme', required=True, choices=['http', 'https'])
    parser.add_argument('--host', required=True)
    parser.add_argument('--port', required=True)
    parser.add_argument('--basepath', required=True)
    parser.add_argument('--client-name', required=True)
    parser.add_argument('--token', required=True)
    parser.add_argument('--cycle', required=True)
    args = parser.parse_args()
    scheme = args.scheme
    host = args.host
    port = args.port
    basepath = args.basepath
    client_name = args.client_name
    token = args.token
    cycle = args.cycle
    url = '%s://%s:%s/%s/updateClient.action?clientid=%s&token=%s' % (scheme, host, port, basepath, client_name, token)
    while True:
        with urllib.request.urlopen(url) as f:
            res = f.read()
        time.sleep(cycle)


if __name__ == '__main__':
    main()