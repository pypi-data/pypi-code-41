""" This module will handle deploying the current environment to a cloud machine """

import argparse
import subprocess
import sys

def deploy():
    parser = argparse.ArgumentParser(
                description='Install packages in the active environment')
    parser.add_argument('--pip', action='store_true',
                        help="Install packages from PyPI with pip")
    parser.add_argument('-p', '--platform', type=str,
                        )


def deploy_aws():
    import boto3 as boto

    client = boto3.client('ec2')