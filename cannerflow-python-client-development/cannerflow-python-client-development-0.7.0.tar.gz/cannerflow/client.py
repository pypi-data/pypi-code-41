# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import cannerflow.workspace
import cannerflow.constants
import cannerflow.exceptions

__all__ = ["bootstrap", "Client"]

def bootstrap(*args, **kwargs):
    return Client(*args, **kwargs)

class Client(object):
    def __init__(self,
        endpoint,
        token,
        workspaceId,
        replaceLocalhostString=None
    ):
        self.workspace = cannerflow.workspace.Workspace(
            endpoint=endpoint,
            headers={
                "Authorization": f"Bearer {token}"
            },
            workspaceId=workspaceId,
            replaceLocalhostString=replaceLocalhostString
        )
    def use_saved_query(self, title):
        query = self.workspace.saved_query.get(title)
        return self.execute(query['sql'])
    def list_saved_query(self):
        return self.workspace.saved_query.list_title()
    def list_file(self):
        return self.workspace.file.list_absolute_path()
    def get_binary(self, absolutePath):
        return self.workspace.file.get_content(absolutePath)
    def get_csv_wrapper(self, absolutePath):
        return self.workspace.file.get_csv_wrapper(absolutePath)
    def get_json_wrapper(self, absolutePath):
        return self.workspace.file.get_json_wrapper(absolutePath)
    def execute(self, sql):
        cursor = self.workspace.statement.execute(sql);
        return cursor
