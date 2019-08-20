# (c) 2017-2019, Tal Shany <tal.shany@biSkilled.com>
#
# This file is part of dingDong
#
# dingDong is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# dingDong is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with dingDong.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import  (absolute_import, division, print_function)
__metaclass__ = type

import logging

class config:
    CONN_URL    =  {    'sql'    :"DRIVER={SQL Server};SERVER=server,1433;DATABASE=database;UID=uid;PWD=pass;",
                        'oracle' :"DRIVER={SQL Server};SERVER=server,1433;DATABASE=database;UID=uid;PWD=pass;",
                        'mysql'  :"host=host, user=user, passwd=pass, db=db",
                        'vertica':"DRIVER=HPVertica;SERVER=server;DATABASE=database;PORT=5433;UID=user;PWD=pass",
                        'file'   :{'delimiter':',','header':True, 'folder':""}
                   }

    QUERY_PARAMS    = {}
    SQL_FOLDER_DIR  = None
    PARSER_SQL_MAIN_KEY = "dingDong"

    DECODE          = "windows-1255"
    TRACK_HISTORY   = True
    LOOP_ON_ERROR   = True
    NUM_OF_PROCESSES= 4

    #LOGGING Properties
    LOGS_DEBUG = logging.DEBUG
    LOGS_DIR   = None
    LOGS_INFO_NAME = 'log'
    LOGS_ERR_NAME  = 'log'
    LOGS_TMP_NAME  = 'lastLog'
    LOGS_HISTORY_DAYS=5

    #SMTP and massaging Configuration
    SMTP_SERVER             = ""
    SMTP_SERVER_USER        = ""
    SMTP_SERVER_PASS        = ""
    SMTP_SENDER             = ""
    SMTP_RECEIVERS          = ['info@biSkilled.com']