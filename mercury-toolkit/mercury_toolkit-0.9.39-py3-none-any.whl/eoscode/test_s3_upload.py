#!/usr/bin/env python

'''
Usage:
    test_s3_upload --config <configfile> --file <filename> --bucket <bucket_name>
'''

import os, sys
import boto3
from snap import snap, common
from eos_datastores import RedshiftS3Context
import docopt


def main(args):
    print(common.jsonpretty(args))

    configfile = args['<configfile>']

    yaml_config = common.read_config_file(configfile)
    services = common.ServiceObjectRegistry(snap.initialize_services(yaml_config))

    file_to_upload = args['<filename>']
    bucket_name = args['<bucket_name>']

    s3_svc = services.lookup('s3')
    key = s3_svc.upload_object(file_to_upload, bucket_name)
    print(key.uri)
    #s3_context = RedshiftS3Context()



if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)
    

