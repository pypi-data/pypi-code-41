# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['data_linter']

package_data = \
{'': ['*'], 'data_linter': ['data/*', 'templates/*']}

install_requires = \
['great-expectations>=0.7.0,<0.8.0',
 'jsonschema>=3.0.0,<3.1.0',
 'pandas>=0.25.0,<0.26.0',
 'parameterized>=0.7.0,<0.8.0',
 'pyarrow>=0.14.0,<0.15.0',
 'tabulate>=0.8.0,<0.9.0']

setup_kwargs = {
    'name': 'data-linter',
    'version': '0.1.0',
    'description': 'A python package that validates datasets against a metadata schema',
    'long_description': '# data_linter\n\nA python package that validates datasets against a metadata schema which is defined [here](https://github.com/moj-analytical-services/data_linter/blob/master/data_linter/data/metadata_jsonschema.json).\n\nIt performs the following checks:\n- Are the columns of the correct data types (or can they be converted without error using `pd.Series.astype` in the case of untyped data formats like `csv`)\n- Column names:\n    - Are the columns named correctly?\n    - Are they in the same order specified in the meta data\n    - Are there any missing columns?\n- Where a regex `pattern` is provided in the metadata,  does the actual data always fit the `pattern`\n- Where an `enum` is provided in the metadata, does the actual data contain only values in the `enum`\n- Where `nullable` is set to false in the metadata, are there really no nulls in the data?\n\nThe package also provides functionality to `impose_metadata_types_on_pd_df`, which allows the user to safely convert a pandas dataframe to the datatypes specified in the metadata.  This is useful in the case you have an untyped data file such as a `csv` and want to ensure it is conformant with the metadata.\n\n## Usage\n\nFor detailed information about how to use the package, please see the [demo repo](https://github.com/moj-analytical-services/data_linter_demo).  This includes an interactive tutorial that you can run in your web browser.\n\nHere\'s a very basic example\n\n```\nimport pandas as pd\nimport json\n\nfrom data_linter.lint import Linter\n\ndef read_json_from_path(path):\n    with open(path) as f:\n        return_json = json.load(f)\n    return return_json\n\nmeta = read_json_from_path("tests/meta/test_meta_cols_valid.json")\ndf = pd.read_parquet("tests/data/test_parquet_data_valid.parquet")\nl = Linter(df, meta)\nl.check_all()\nl.markdown_report()\n```',
    'author': 'Karik Isichei',
    'author_email': 'karik.isichei@digital.justice.gov.uk',
    'url': 'https://github.com/moj-analytical-services/data_linter',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
