# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ife',
 'ife.data',
 'ife.features',
 'ife.features.tests',
 'ife.io',
 'ife.io.tests',
 'ife.util',
 'ife.util.tests']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=6.1,<7.0', 'colour-science>=0.3.13,<0.4.0', 'pandas>=0.25.0,<0.26.0']

setup_kwargs = {
    'name': 'ife',
    'version': '0.0.3',
    'description': 'You can get a nice global image feature!',
    'long_description': '# Image Feature Extractor(IFE)\n[![Coverage Status](https://coveralls.io/repos/github/Collonville/ImageFeatureExtractor/badge.svg)](https://coveralls.io/github/Collonville/ImageFeatureExtractor)\n[![Build Status](https://travis-ci.org/Collonville/ImageFeatureExtractor.svg?branch=develop)](https://travis-ci.org/Collonville/ImageFeatureExtractor)\n[![Codacy Badge](https://api.codacy.com/project/badge/Grade/115c65043153459cbfc5026ea53be08d)](https://www.codacy.com/app/Collonville/ImageFeatureExtractor?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Collonville/ImageFeatureExtractor&amp;utm_campaign=Badge_Grade)\n[![PyPI version](https://badge.fury.io/py/ife.svg)](https://badge.fury.io/py/ife)\n\n## What is this\n`IFE` is a package to get an image feature more easily for Python. It contains many kinds of feature extract algorithms.\n\n## Insatall\n   For the latest version are available using pip install.\n```bash\npip install ife\n```\n\n## 1. Features\n### Color Moment\n-   Mean, Median, Variance, Skewness, Kurtosis of `RGB, HSV, HSL, CMY`\n### Colourfulness\n-   Colourfulness measure of the image\n\n## 2. Examples\nImport the basic image reader of IFE.\n```python\nfrom ife.io.io import ImageReader\n```\n\n### 2.1 Get Moment\nAdd a image file path to `read_from_single_file()`. This will return basic features class.\n\nAnd now! You can get a RGB color moment feature from image!!\n\n### Sample\n```python\n>>> features = ImageReader.read_from_single_file("ife/data/small_rgb.jpg")\n>>> features.moment()\narray([[ 0.57745098,  0.52156863,  0.55980392],\n       [ 0.58823529,  0.48823529,  0.54901961],\n       [ 0.15220588,  0.12136101,  0.12380911],\n       [-0.01944425,  0.18416571,  0.04508015],\n       [-1.94196824, -1.55209335, -1.75586748]])\n```\n\nAlso, you can get an `flatten vector, dictionary, or pandas`\n```python\n>>> features.moment(output_type="one_col")\narray([ 0.57745098,  0.52156863,  0.55980392,  0.58823529,  0.48823529,\n        0.54901961,  0.15220588,  0.12136101,  0.12380911, -0.01944425,\n        0.18416571,  0.04508015, -1.94196824, -1.55209335, -1.75586748])\n\n>>> features.moment(output_type="dict")\ndefaultdict(<class \'dict\'>, {\'mean\': {\'R\': 0.57745098039215681, \'G\': 0.52156862745098043, \'B\': 0.55980392156862746}, \'median\': {\'R\': 0.58823529411764708, \'G\': 0.48823529411764705, \'B\': 0.5490196078431373}, \'var\': {\'R\': 0.15220588235294119, \'G\': 0.12136101499423299, \'B\': 0.12380911188004615}, \'skew\': {\'R\': -0.019444250980856902, \'G\': 0.18416570783012232, \'B\': 0.045080152334687214}, \'kurtosis\': {\'R\': -1.9419682406751135, \'G\': -1.5520933544103905, \'B\': -1.7558674751807395}})\n\n>>> features.moment(output_type="pandas")\n       mean    median       var      skew  kurtosis\nR  0.577451  0.588235  0.152206 -0.019444 -1.941968\nG  0.521569  0.488235  0.121361  0.184166 -1.552093\nB  0.559804  0.549020  0.123809  0.045080 -1.755867\n```\n\n> No! I want a HSV Color space feature :(\n\nIt can set another color space! Default will be RGB.\n```python\n>>> features.moment(output_type="one_col", color_space="CMY")\narray([ 0.42254902,  0.47843137,  0.44019608,  0.41176471,  0.51176471,\n        0.45098039,  0.15220588,  0.12136101,  0.12380911,  0.01944425,\n       -0.18416571, -0.04508015, -1.94196824, -1.55209335, -1.75586748])\n       \n>>> features.moment(output_type="dict", color_space="HSL")\ndefaultdict(<class \'dict\'>, {\'mean\': {\'H\': 0.50798329143793874, \'S\': 0.52775831413836383, \'L\': 0.61421568627450984}, \'median\': {\'H\': 0.51915637553935423, \'S\': 0.62898601603182969, \'L\': 0.52156862745098043}, \'var\': {\'H\': 0.13290200013401141, \'S\': 0.10239897927552907, \'L\': 0.051550124951941563}, \'skew\': {\'H\': -0.078898095002588917, \'S\': -0.83203104238315984, \'L\': 1.0202366337483093}, \'kurtosis\': {\'H\': -1.2599104562470791, \'S\': -0.87111810912637022, \'L\': -0.7502836585891588}})\n\n>>> features.moment(output_type="pandas", color_space="HSV")\n       mean    median       var      skew  kurtosis\nH  0.507983  0.519156  0.132902 -0.078898 -1.259910\nS  0.595236  0.749543  0.122723 -1.028366 -0.768867\nV  0.855882  0.864706  0.013867 -0.155656 -1.498179\n```\n## 2.2 Colourfulness\n### Reference\nD. Hasler and S.E.Suesstrunk, ``Measuring colorfulness in natural images," Human\nVision andElectronicImagingVIII, Proceedings of the SPIE, 5007:87-95, 2003.\n\n### Sample\n```python\n>>> features = ImageReader.read_from_single_file("ife/data/strawberry.jpg")\n>>> features.colourfulness()\n0.18441700366624714\n```\n\n## 3. Future work\n### IO\n-   Read from URL links\n-   Read from Base64\n-   Sliding window\n-   Video files\n\n### Color space\n-   CMYK\n-   CIE Lab\n-   XYZ\n\n### Features\n-   Value normalize\n-   Average Gradient\n-   LBP\n-   Histogram\n-   Color harmony\n-   Entropy\n-   Brightness measure\n-   Contrast measure\n-   Saturation measure\n-   Naturalness\n-   Color fidelity metric\n-   Saliency map\n-   Fisher vector\n-   VGG16, 19 layer feature\n-   and more...\n\n## 4. Author\n@Collonville\n\n## 5. Licence\nBSD-3-Clause\n',
    'author': 'HokutoTateyama',
    'author_email': 'ht235711@yahoo.co.jp',
    'url': 'https://github.com/Collonville/ImageFeatureExtractor',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
