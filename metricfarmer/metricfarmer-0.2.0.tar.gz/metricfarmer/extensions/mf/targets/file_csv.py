import csv
import datetime
import os

from metricfarmer.exceptions import ExtensionException


def target_file_csv(metrics, **kwargs):
    if 'path' not in kwargs:
        raise ExtensionException('Path parameter must be specified for mf.file_csv')

    path = kwargs['path']
    override = kwargs.get('override', False)
    delimiter = kwargs.get('delimiter', ',')

    orig_data = {}

    if os.path.exists(path) and not override:
        with open(path, 'r') as csv_file:
            reader = csv.DictReader(csv_file, delimiter=delimiter)
            headers = reader.fieldnames
            for row in reader:
                orig_data[row['metric']] = row
    else:
        headers = ['metric']

    timestamp = datetime.datetime.now().replace(microsecond=0).isoformat()
    updated_data = orig_data
    for name, metric in metrics.items():
        if name in updated_data.keys():
            updated_data[name][timestamp] = metric['result']
        else:
            updated_data[name] = {'metric': name, timestamp: metric['result']}

    # Update headers with newest timestamp for current data
    headers.append(timestamp)

    with open(path, 'w') as csv_file:
        writer = csv.DictWriter(csv_file, headers, delimiter=delimiter)
        writer.writeheader()
        writer.writerows(updated_data.values())
