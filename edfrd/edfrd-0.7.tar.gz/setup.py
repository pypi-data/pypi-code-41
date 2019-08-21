# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['edfrd']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.15,<2.0']

setup_kwargs = {
    'name': 'edfrd',
    'version': '0.7',
    'description': 'edfrd is a Python 3 software library to read and write EDF files.',
    'long_description': "# edfrd\n\nedfrd is a Python 3 software library to **read** and **write** EDF files.\n\nIt is designed as a low-level library, that does not interpret the EDF data whenever possible. Therefore, edfrd can\nread files even if non-standard values are contained in the header.\n\nData records are loaded as `int16` arrays using numpy.\n\n\n## Installation\n\n```bash\npip3 install --user edfrd\n```\n\n\n## Reading EDF Header and Data Records\n\n```python\nfrom edfrd import read_header, read_data_records\n\nfile_path = 'PATH/TO/FILE.edf'\n\nheader = read_header(file_path)\nprint(header)\n\nfor data_record in read_data_records(file_path, header):  # generator\n    # iterate through data_records\n    break\n\nfor signal in data_record:\n    # iterate through signal arrays of a single data_record\n    print(signal.size)\n\nfor signal_header, signal in zip(header.signals, data_record):\n    # iterate through signal headers and signal arrays\n    print(signal_header.label, signal.size)\n```\n\nIf the header of your EDF file does not correctly specifiy the number of data records, you can use the following option\nto calculate it from the file size.\n\n```python\nheader = read_header(file_path, calculate_number_of_data_records=True)\n```\n\nYou can try parsing the `startdate_of_recording` and `starttime_of_recording` as integer tuples. If parsing fails the\noriginal string will be returned.\n\n```python\nheader = read_header(file_path, parse_date_time=True)\n\nday, month, year = header.startdate_of_recording\nhours, minutes, seconds = header.starttime_of_recording\n```\n\nThe number of data records being read can be limited by specifying an optional `start` or `end` index.\n\n```python\nfor data_record in read_data_records(file_path, header, start=0, end=header.number_of_data_records):\n    break\n```\n\nTo work with larger chunks of a signal than provided by a data record, consider creating a new numpy array as a\n`buffer`.\n\n```python\nimport numpy as np\nfrom edfrd import read_header, read_data_records\n\nfile_path = 'PATH/TO/FILE.edf'\n\nheader = read_header(file_path)\nstart, end = 2, 4\nsignal_index = 0\nsignal_header = header.signals[signal_index]\nbuffer_length = (end - start) * signal_header.nr_of_samples_in_each_data_record\nbuffer = np.empty(buffer_length, dtype=np.int16)\npointer = 0\n\nfor data_record in read_data_records(start, end):\n    buffer[pointer:pointer+signal_header.nr_of_samples_in_each_data_record] = data_record[signal_index]\n    pointer += signal_header.nr_of_samples_in_each_data_record\n\nprint(buffer)\n```\n\nYou can also pass a file descriptor (`fr`) instead of a string (`file_path`). Note that `read_data_records` will\ncontinue from the current byte position, where `read_header` stopped, without performing an additional seek operation.\n\n```python\nwith open(file_path, 'rb') as fr:\n    header = read_header(fr)\n\n    for data_record in read_data_records(fr, header):\n        break\n```\n\n\n## Writing EDF Header and Data Records\n\n```python\nfrom edfrd import read_header, read_data_records, write_header, write_data_records\n\nfile_path = 'PATH/TO/FILE.edf'\nnew_file_path = 'PATH/TO/NEW_FILE.edf'\n\nheader = read_header(file_path)\ndata_records = read_data_records(file_path, header)\nwrite_header(file_path, header)\nwrite_data_records(file_path, data_records)\n```\n\nAgain, using file descriptors (`fr` and `fw`) is possible.\n\n```python\nwith open(file_path, 'rb') as fr:\n    header = read_header(fr)\n    data_records = read_data_records(fr, header)\n    \n    with open(new_file_path, 'wb') as fw:\n        write_header(fw, header)\n        write_data_records(fw, data_records)\n```\n",
    'author': 'Christoph Jansen',
    'author_email': 'Christoph.Jansen@htw-berlin.de',
    'url': 'https://cbmi.htw-berlin.de/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
