'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

import argparse
import os

import microdns


def _path(exists, arg):
    path = os.path.abspath(arg)
    if not os.path.exists(path) and exists:
        msg = '"{0}" is not a valid path'.format(path)
        raise argparse.ArgumentTypeError(msg)
    return path


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("ip", type=str, default="127.0.0.1", help="Interface")
    parser.add_argument("port", type=int,
                        help="port uDNS should listen on")
    parser.add_argument("zone_file", type=lambda x: _path(
        True, x), help="path to zone file")
    parser.add_argument("--rr", action='store_true',
                        help='round robin load balances if multiple IP addresses are present for 1 domain')

    args = parser.parse_args()

    server = microdns.MicroDNS(args.zone_file, args.port, args.ip, args.rr)

    server.serve_forever()


if __name__ == '__main__':
    main()
