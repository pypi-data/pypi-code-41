#!/usr/bin/env python

import json
import eos_datastores as eds


def test_frame_transform(dataframe, service_registry, **kwargs):
    #postgres_svc = service_registry.lookup('postgres')
    return dataframe


def console_frame_writer(dataframe, service_registry, **kwargs):
    #print(dataframe)
    #print('subbed write function.')

    #redshift_svc = service_registry.lookup('redshift')
    #with redshift_svc.txn_scope() as session:
    records_to_import = []
    for _, record in dataframe.iterrows():
        records_to_import.append(record)

    #print(records_to_import)
    rds = eds.ABCDatastore(service_registry)
    rds.bulk_write(records_to_import)

