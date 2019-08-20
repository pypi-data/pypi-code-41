# -*- coding: utf-8 -*-

#  Copyright 2019-  DNB
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import six
from rbfExcel.base import ExcelLibrary
from rbfExcel.version import __version__
from rbfExcel.utils import DateFormat, NumberFormat, BoolFormat




class rbfExcel(ExcelLibrary):
    """
    rbfExcel library provides some keywords to allow opening, reading, writing, and saving Excel files from Robot Framework.

    *Before running tests*

    Prior to running tests, rbfExcel must first be imported into your Robot test suite.

    Example:
        | Library | rbfExcel |

    To setup some Excel configurations related to date format and number format, use these arguments

        *Excel Date Time format*
        | Date Format       | Default: `yyyy-mm-dd`         |
        | Time Format       | Default: `HH:MM:SS AM/PM`     |
        | Date Time Format  | Default: `yyyy-mm-dd HH:MM`   |
        For more information, check this article
        https://support.office.com/en-us/article/format-numbers-as-dates-or-times-418bd3fe-0577-47c8-8caa-b4d30c528309

        *Excel Number format*
        | Decimal Separator     | Default: `.`  |
        | Thousand Separator    | Default: `,`  |
        | Precision             | Default: `2`  |

        *Excel Boolean format*
        | Boolean Format        | Default: `Yes/No`  |

    Example:
        | Library | rbfExcel | date_format='dd/mm/yyyy'
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__

    def __init__(self,
                 date_format='yyyy-mm-dd', time_format='HH:MM:SS AM/PM', datetime_format='yyyy-mm-dd HH:MM',
                 decimal_sep='.', thousand_sep=',', precision='2', bool_format='Yes/No'):
        logging.basicConfig()
        logging.getLogger().setLevel(logging.INFO)
        logger = logging.getLogger(__name__)
        logger.info('rbfExcel::Robotframework Excel Library')
        super(rbfExcel, self).__init__(
            DateFormat(date_format, time_format, datetime_format),
            NumberFormat(decimal_sep, thousand_sep, precision),
            BoolFormat(bool_format))
