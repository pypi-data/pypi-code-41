#!/usr/bin/env python3

import argparse
import json
import os
import sys
import io
import gzip
import traceback

import mistune
import requests
import ruamel.yaml
from colorama import Back, Fore, Style
# import yaml
from packaging import version

from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib import request

import pkg_resources
from pyfiglet import Figlet


def main():
    def parse_cl_md(file_data):
        bs = BeautifulSoup(mistune.markdown(file_data), features="lxml")
        changelog = {}
        hTag = None
        for row in bs.findAll('h1'):
            if isinstance(version.parse(row.text), version.Version):
                hTag = 'h1'
                break
        if hTag == None:
            for row in bs.findAll('h2'):
                if isinstance(version.parse(row.text), version.Version):
                    hTag = 'h2'
                    break

        if hTag == None:
            return None

        for row in bs.findAll(hTag):
            v = row.text
            changes = []
            ulTag = row.find_next_sibling('ul')
            for liTag in ulTag.findAll('li'):
                changes.append(liTag.text.replace('\n', ' '))
            changelog[v] = changes
        return changelog

    def get_cl(homepage):
        o = urlparse(homepage)
        if o.netloc != 'github.com':
            return None
        # api_url = f'https://raw.githubusercontent.com{o.path.replace("/tree/", "/blob/master/")}/master/CHANGELOG.md'
        if "/blob/" in homepage or "/tree/" in homepage:
            api_url = homepage.replace(
                "/blob/", "/raw/").replace("/tree/", "/raw/")
        else:
            api_url = homepage + "/raw/master"
        api_url += "/CHANGELOG.md"
        response = requests.get(api_url)

        if response.status_code == 200:
            return parse_cl_md(response.content.decode('utf-8'))
        else:
            return None

    def get_cl_from_archive(url):
        response = request.urlopen(url)
        compressed_file = io.BytesIO(response.read())
        decompressed_file = gzip.GzipFile(fileobj=compressed_file)

    def print_cl(cl, current_version):
        printed = False
        if isinstance(cl, dict):
            for v in cl:
                if version.parse(v) > current_version:
                    print(f'{Fore.YELLOW}[{v}]{Style.RESET_ALL}')
                    printed = True
                    for item in cl[v]:
                        print(f' * {item}')
                        printed = True
        if not printed:
            print(f'{Fore.YELLOW}Unable to determine changelog{Style.RESET_ALL}')

    def is_dir(dirname):
        fname = os.path.abspath(dirname) + '/pubspec.yaml'
        if not os.path.isdir(dirname):
            msg = "{0} is not a directory".format(dirname)
            raise argparse.ArgumentTypeError(msg)
        elif not os.path.isfile(fname):
            msg = "{0} does not contain pubspec.yaml".format(dirname)
            raise argparse.ArgumentTypeError(msg)
        else:
            return dirname

    def get_args():
        app_version = pkg_resources.require("pubupd")[0].version
        f = Figlet(font='slant')
        print(f.renderText('pubupd'))
        print(f'v{app_version}')
        parser = argparse.ArgumentParser(
            description=f'Utility to update dependencies in flutter project\'s pubspec.yaml')

        parser.add_argument('dir', help="The directory of flutter project containing pubspec.yaml", nargs=1,
                            type=is_dir, )
        parser.add_argument('-c', '--change-log',
                            action='store_true', help="Display changelog")
        parser.add_argument('-a', '--display-all',
                            action='store_true', help="Display all packages including updated ones")
        parser.add_argument('-u', '--update-pubspec',
                            action='store_true', help="Update pubspec.yaml file with latest versions")
        parser.add_argument('-i', '--install',
                            nargs='?', help="Install new dependency in pubspec.yaml")

        return parser.parse_args()

    def get_package_info(package):
        api_url = 'https://pub.dev/api/packages/' + package
        response = requests.get(api_url)

        if response.status_code == 200:
            return json.loads(response.content.decode('utf-8'))
        else:
            return None

    def update_pubspec(data, args):
        dep = data['dependencies']
        for package in dep:
            if type(dep[package]) is dict:
                continue
            if type(dep[package]) is not str:
                continue
            package_info = get_package_info(package)
            # print(package_info['latest']['pubspec'])
            cv = version.parse(dep[package].replace('^', ''))
            lv = version.parse(package_info['latest']['version'])
            homepage = package_info['latest']['pubspec']['homepage']
            outdated = lv > cv
            if outdated:
                data['dependencies'][package] = '^' + str(lv)
                print(
                    f'{Fore.BLUE}[{package}]{Style.RESET_ALL} {Fore.RED}{str(cv)}{Style.RESET_ALL} -> {Fore.GREEN}{str(lv)}{Style.RESET_ALL} (Update available)')
                if args.change_log:
                    cl = get_cl(homepage)
                    print_cl(cl, cv)
            elif args.display_all:
                print(
                    f'{Fore.BLUE}[{package}]{Style.RESET_ALL} {Fore.GREEN}{str(cv)}{Style.RESET_ALL} (latest)')
        return data, None

    def add_dependency(data, package):
        package_info = get_package_info(package)
        if package_info is None:
            return data, 'No such package exists'

        lv = version.parse(package_info['latest']['version'])
        data['dependencies'][package] = '^' + str(lv)
        print(
            f'Adding {package} version {Fore.GREEN}{str(lv)}{Style.RESET_ALL} to pubspec.yaml')
        return data, None

    def run():
        args = get_args()
        project = os.path.abspath(args.dir[0])
        fname = project + '/pubspec.yaml'
        stream = open(fname, 'r')
        yaml = ruamel.yaml.YAML()  # defaults to round-trip if no parameters given
        data = yaml.load(stream)
        err = None
        if args.install is not None:
            data, err = add_dependency(data, args.install)
        else:
            data, err = update_pubspec(data, args)

        if err is not None:
            print(f'{Fore.RED}{err}{Style.RESET_ALL}')
            sys.exit(1)

        if args.update_pubspec:
            new_file = open(project + "/pubspec.yaml", 'w')
            yaml.dump(data, new_file)

    try:
        run()
    except KeyboardInterrupt:
        print("Shutdown requested...exiting")
    except Exception:
        traceback.print_exc(file=sys.stdout)
    sys.exit(0)
