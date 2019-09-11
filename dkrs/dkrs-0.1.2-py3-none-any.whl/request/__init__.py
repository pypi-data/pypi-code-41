# Copyright (C) 2019 Erhu Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests

from dkrs.log import log, error


class Requests:

    def __init__(self, url):
        self.url = url

    def get(self):
        return requests.get(self.url)

    def post_json(self, data):
        if data:
            log("POST_JSON: URL -> {}, DATA -> {}".format(self.url, data))
            result = requests.post(self.url, json=data)
            log("RESULT: code:{}, reason:{}, text:{}".format(result.status_code,
                                                             result.reason,
                                                             result.text))
            return result
        else:
            error('Data is None when post_json')
            return None
