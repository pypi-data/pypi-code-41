#!/usr/bin/env python

'''
Usage:
    dfwrite --config <configfile> 

'''

import os, sys
import json
from snap import snap, common
import pandas as pd
import docopt


def main(args):
    config_filename = args['<configfile>']
    yaml_config = common.read_config_file(config_filename)
    service_registry = common.ServiceObjectRegistry(snap.initialize_services(yaml_config))

    input = [{'id':1, 'testfield':"Hello"}, {'id':2,'testfield':"World"}, {'id':3,'testfield':'we are here'}]
    df = pd.DataFrame(input)
    
    for _, row in df.iterrows():
        record = {
            'id': row['id'],
            'testfield': row['testfield']
        }
        print(json.dumps(record))
    

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)