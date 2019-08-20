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

import re
import sys

from dingDong.config import config

def replaceStr (sString,findStr, repStr, ignoreCase=True,addQuotes=None):
    if addQuotes and isinstance(repStr,str):
        repStr="%s%s%s" %(addQuotes,repStr,addQuotes)

    if ignoreCase:
        pattern = re.compile(re.escape(findStr), re.IGNORECASE)
        res = pattern.sub (repStr, sString)
    else:
        res = sString.replace (findStr, repStr)
    return res

def uniocdeStr (sObj, decode=False):
    if 3 == sys.version_info[0]:
        return sObj

    return unicode (str(sObj).decode(config.DECODE)) if decode else unicode (sObj)
