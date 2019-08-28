# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['kiwi',
 'kiwi.cli',
 'kiwi.cli.models',
 'kiwi.cli.pipelines',
 'kiwi.data',
 'kiwi.data.fields',
 'kiwi.data.fieldsets',
 'kiwi.lib',
 'kiwi.metrics',
 'kiwi.models',
 'kiwi.models.linear',
 'kiwi.models.modules',
 'kiwi.predictors',
 'kiwi.trainers']

package_data = \
{'': ['*']}

install_requires = \
['configargparse>=0.14.0,<0.15.0',
 'more-itertools>=5.0,<6.0',
 'numpy>=1.16,<2.0',
 'pyyaml>=3.13,<4.0',
 'scipy>=1.2,<2.0',
 'torch>=0.4.1',
 'torchtext>=0.3.1,<0.4.0',
 'tqdm>=4.29,<5.0']

extras_require = \
{':python_version == "3.5"': ['pathlib2>=2.3,<3.0'],
 'embeddings': ['polyglot>=16.7,<17.0'],
 'mlflow': ['mlflow>=0.8,<0.9'],
 'plots': ['seaborn>=0.9.0,<0.10.0']}

entry_points = \
{'console_scripts': ['kiwi = kiwi.__main__:main']}

setup_kwargs = {
    'name': 'openkiwi',
    'version': '0.1.2',
    'description': 'Machine Translation Quality Estimation Toolkit',
    'long_description': "![OpenKiwi Logo](https://github.com/Unbabel/OpenKiwi/blob/master/docs/_static/img/openkiwi-logo-horizontal.svg)\n\n--------------------------------------------------------------------------------\n\n[![PyPI version](https://img.shields.io/pypi/v/openkiwi?color=%236ecfbd&label=pypi%20package&style=flat-square)](https://pypi.org/project/openkiwi/)\n[![python versions](https://img.shields.io/pypi/pyversions/openkiwi.svg?style=flat-square)](https://pypi.org/project/openkiwi/)\n[![CircleCI](https://img.shields.io/circleci/build/github/Unbabel/OpenKiwi/master?style=flat-square)](https://circleci.com/gh/Unbabel/OpenKiwi/tree/master)\n[![Code Climate coverage](https://img.shields.io/codeclimate/coverage/Unbabel/OpenKiwi?style=flat-square)](https://codeclimate.com/github/Unbabel/OpenKiwi/test_coverage)\n![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)\n\n**Open-Source Machine Translation Quality Estimation in PyTorch**\n\nQuality estimation (QE) is one of the missing pieces of machine translation: its goal is to evaluate a translation system’s quality without access to reference translations. We present **OpenKiwi**, a Pytorch-based open-source framework that implements the best QE systems from WMT 2015-18 shared tasks, making it easy to experiment with these models under the same framework. Using OpenKiwi and a stacked combination of these models we have achieved state-of-the-art results on word-level QE on the WMT 2018 English-German dataset.\n\n## News\n\nFollowing our nomination in early July, we are happy to announce we won the [Best Demo Paper at ACL 2019](http://www.acl2019.org/EN/winners-of-acl-2019-best-paper-awards.xhtml)! Congratulations to the whole team and huge thanks for supporters and issue reporters.\n\nCheck out the [published paper](https://www.aclweb.org/anthology/P19-3020).\n\nWe are going to release the web interface we had put in place for the live demo presentation at ACL.\n\n## Features\n\n* Framework for training QE models and using pre-trained models for evaluating MT.\n* Supports both word and sentence-level Quality estimation.\n* Implementation of five QE systems in Pytorch: QUETCH [[1]], NuQE [[2], [3]], predictor-estimator [[4], [5]], APE-QE [[3]], and a stacked ensemble with a linear system [[2], [3]]. \n* Easy to use API. Import it as a package in other projects or run from the command line.\n* Provides scripts to run pre-trained QE models on data from the WMT 2018 campaign.\n* Easy to track and reproduce experiments via yaml configuration files.\n\n## Results\n\nResults for the [WMT18 Quality Estimation shared task](http://www.statmt.org/wmt18/quality-estimation-task.html#results), for [word level](https://competitions.codalab.org/competitions/19306#results) *and* [sentence level](https://competitions.codalab.org/competitions/19316#results) on the test set.\n\n|   Model   | En-De SMT |           |           |           |           | En-De NMT |           |           |           |           |\n|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|:---------:|\n|           |     MT    |    gaps   |   source  |     r     |     ⍴     |     MT    |    gaps   |   source  |     r     |     ⍴     |\n|  OpenKiwi | **62.70** | **52.14** | **48.88** |   71.08   |   72.70   | **44.77** | **22.89** | **36.53** |   46.72   |   58.51   |\n|  Wang2018 |   62.46   |   49.99   |     --    | **73.97** | **75.43** |   43.61   |     --    |     --    |   50.12   |   60.49   |\n|    UNQE   |     --    |     --    |     --    |   70.00   |   72.44   |     --    |     --    |     --    | **51.29** | **60.52** |\n| deepQUEST |   42.98   |   28.24   |   33.97   |   48.72   |   50.97   |   30.31   |   11.93   |   28.59   |   38.08   |   48.00   |\n\n\n## Quick Installation\n\nTo install OpenKiwi as a package, simply run\n```bash\npip install openkiwi\n```\n\nYou can now\n```python\nimport kiwi\n```\ninside your project or run in the command line\n```bash\nkiwi\n```\n\n**Optionally**, if you'd like to take advantage of our [MLflow](https://mlflow.org/) integration, simply install it in the same virtualenv as OpenKiwi:\n```bash\npip install mlflow\n```\n\n\n## Getting Started\n\nDetailed usage examples and instructions can be found in the [Full Documentation](https://unbabel.github.io/OpenKiwi/index.html).\n\n\n## Pre-trained models\n\nWe provide pre-trained models with the corresponding pre-processed datasets and configuration files.\nYou can easily reproduce our numbers in the WMT 2018 word- and sentence-level tasks by following the [reproduce instructions in the documentation](https://unbabel.github.io/OpenKiwi/reproduce.html).\n\n\n## Contributing\n\nWe welcome contributions to improve OpenKiwi.\nPlease refer to [CONTRIBUTING.md](CONTRIBUTING.md) for quick instructions or to [contributing instructions](https://unbabel.github.io/OpenKiwi/contributing/contributing.html) for more detailed instructions on how to set up your development environment.\n\n\n## License\n\nOpenKiwi is Affero GPL licensed. You can see the details of this license in [LICENSE](LICENSE).\n\n\n## Citation\n\nIf you use OpenKiwi, please cite the following paper: [OpenKiwi: An Open Source Framework for Quality Estimation](https://www.aclweb.org/anthology/P19-3020).\n\n```\n@inproceedings{openkiwi,\n    author = {Fábio Kepler and\n              Jonay Trénous and\n              Marcos Treviso and\n              Miguel Vera and\n              André F. T. Martins},\n    title  = {Open{K}iwi: An Open Source Framework for Quality Estimation},\n    year   = {2019},\n    booktitle = {Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics--System Demonstrations},\n    pages  = {117--122},\n    month  = {July},\n    address = {Florence, Italy},\n    url    = {https://www.aclweb.org/anthology/P19-3020},\n    organization = {Association for Computational Linguistics},\n}\n```\n\n\n## References\n\n##### [[1]] [Kreutzer et al. (2015): QUality Estimation from ScraTCH (QUETCH): Deep Learning for Word-level Translation Quality Estimation](http://aclweb.org/anthology/W15-3037)\n[1]:#1-kreutzer-et-al-2015-quality-estimation-from-scratch-quetch-deep-learning-for-word-level-translation-quality-estimation\n\n##### [[2]] [Martins et al. (2016): Unbabel's Participation in the WMT16 Word-Level Translation Quality Estimation Shared Task](http://www.aclweb.org/anthology/W16-2387)\n[2]:#2-martins-et-al-2016-unbabels-participation-in-the-wmt16-word-level-translation-quality-estimation-shared-task\n\n##### [[3]] [Martins et al. (2017): Pushing the Limits of Translation Quality Estimation](http://www.aclweb.org/anthology/Q17-1015)\n[3]:#3-martins-et-al-2017-pushing-the-limits-of-translation-quality-estimation\n\n##### [[4]] [Kim et al. (2017): Predictor-Estimator using Multilevel Task Learning with Stack Propagation for Neural Quality Estimation](http://www.aclweb.org/anthology/W17-4763)\n[4]:#4-kim-et-al-2017-predictor-estimator-using-multilevel-task-learning-with-stack-propagation-for-neural-quality-estimation\n\n##### [[5]] [Wang et al. (2018): Alibaba Submission for WMT18 Quality Estimation Task](http://statmt.org/wmt18/pdf/WMT093.pdf)\n[5]:#5-wang-et-al-2018-alibaba-submission-for-wmt18-quality-estimation-task\n",
    'author': 'AI Research, Unbabel',
    'author_email': 'openkiwi@unbabel.com',
    'url': 'https://github.com/Unbabel/OpenKiwi',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
