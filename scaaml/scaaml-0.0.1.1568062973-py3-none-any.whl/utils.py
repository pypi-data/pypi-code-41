# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from termcolor import cprint, colored


def pretty_hex(val):
    "convert a value into a pretty hex"
    s = hex(int(val))
    s = s[2:]  # remove 0x
    if len(s) == 1:
        s = '0' + s
    return s


def hex_display(lst, prefix="", color='green'):
    "display a list of int as colored hex"
    h = []

    for e in lst:
        h.append(pretty_hex(e))
    cprint(prefix + " ".join(h), color)


def hex_display_recovered_key(recovered_key, real_key, prefix=""):
    "display the recovered key as colored hex based of success"
    rkey = []
    for idx in range(len(recovered_key)):
        v = pretty_hex(recovered_key[idx])
        if recovered_key[idx] == real_key[idx]:
            rkey.append(colored(v, 'green'))
        else:
            rkey.append(colored(v, 'red'))
    print(prefix + " ".join(rkey))
