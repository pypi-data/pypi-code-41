# Copyright 2019-     DNB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from .RequestsKeywords import RequestsKeywords
from .version import __version__


class rbfHTTP(RequestsKeywords):
    """ rbfHTTP is a HTTP client library

        Examples:
        
        *GET Requests*
        
        | `Create Session` | google | http://www.google.com |
        | `Create Session` | github | https://api.github.com | verify=${CURDIR}${/}cacert.pem |
        | ${resp}= | `Get Request` | google |  / |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${resp}= | `Get Request` | github | /users/bulkan |
        | `Should Be Equal As Strings` |  ${resp.status_code} | 200 |
        | `Dictionary Should Contain Value` | ${resp.json()} | Bulkan Evcimen |
        
        *GET Request with URL Parameters*
        
        | `Create Session` | httpbin | http://httpbin.org  |  
        | &{params}= | `Create Dictionary` | key=value | key2=value2 |  
        | ${resp}= | `Get Request` | httpbin | /get | params=${params} |  
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |  
        | ${jsondata}= | `To Json` | ${resp.content} |  
        | `Should Be Equal` | ${jsondata['args']} | ${params} |  
        
        *GET Request with JSON Data*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{data}= | `Create Dictionary` |  latitude=30.496346 | longitude=-87.640356 |  
        | ${resp}= | `Get Request` | httpbin | /get | json=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${jsondata}= | `To Json` | ${resp.content} |
        
        *GET Request (HTTPS) and verify cert*
        
        | `Create Session` | httpbin | https://httpbin.org | verify=True |
        | ${resp}= | `Get Request` | httpbin | /get |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *GET Request (HTTPS) and verify cert with CA bundle*
        
        | `Create Session` | httpbin | https://httpbin.org |  verify=${CURDIR}${/}cacert.pem |
        | ${resp}= | `Get Request` | httpbin | /get |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *GET Request (HTTPS) with client side certificates*
        
        | @{client_certs}= | `Create List` | ${CURDIR}${/}clientcert.pem | ${CURDIR}${/}clientkey.pem |
        | `Create Client Cert Session` | crtsession | https://server.cryptomix.com/secure | client_certs=@{client_certs} |
        | ${resp}= | `Get Request` | crtsession | / |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *GET Request with Auth*
        
        | ${auth}= | `Create List` | user |  passwd |
        | `Create Session` | httpbin | https://httpbin.org | auth=${auth} | verify=${CURDIR}${/}cacert.pem |
        | ${resp}= | `Get Request` | httpbin | /basic-auth/user/passwd |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | `Should Be Equal As Strings` | ${resp.json()['authenticated']} | True |
        
        *GET Request with Custom Auth*
        
        | ${auth}= | `Get Custom Auth` | user |  passwd | 
        | `Create Custom Session` | httpbin | https://httpbin.org | auth=${auth} | verify=${CURDIR}${/}cacert.pem | 
        | ${resp}= | `Get Request` | httpbin | /basic-auth/user/passwd | 
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 | 
        | `Should Be Equal As Strings` | ${resp.json()['authenticated']} | True | 
        
        *GET Request with Digest Auth*
        
        | ${auth}= | `Create List` | user | pass | 
        | `Create Digest Session` | httpbin | https://httpbin.org | auth=${auth} | debug=3 | verify=${CURDIR}${/}cacert.pem | 
        | ${resp}= | `Get Request` | httpbin | /digest-auth/auth/user/pass | 
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 | 
        | `Should Be Equal As Strings` | ${resp.json()['authenticated']} | True | 
        
        *GET Request with Redirection*
        
        | `Create Session` | httpbin | http://httpbin.org | debug=3 |
        | ${resp}= | `Get Request` | httpbin | /redirect/1 |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${resp}= | `Get Request` | httpbin | /redirect/1 | allow_redirects=${true} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *GET Request without Redirection*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Get Request` | httpbin | /redirect/1 | allow_redirects=${false} |
        | ${status}= | `Convert To String` | ${resp.status_code} |
        | `Should Start With` | ${status} | 30 |        
        
        *POST Requests*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{data}= | `Create Dictionary` | name=bulkan | surname=evcimen |
        | &{headers}= | `Create Dictionary` | Content-Type=application/x-www-form-urlencoded |
        | ${resp}= | `Post Request` | httpbin | /post | data=${data} | headers=${headers} |
        | `Dictionary Should Contain Value` | ${resp.json()['form']} | bulkan |
        | `Dictionary Should Contain Value` | ${resp.json()['form']} | evcimen |
                
        *POST Request with File*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${file_data}= | `Get Binary File` | ${CURDIR}${/}data.json |
        | &{files}= | `Create Dictionary` | file=${file_data} |
        | ${resp}= | `Post Request` | httpbin | /post | files=${files} |
        | ${file}= | `To Json` | ${resp.json()['files']['file']} |
        | `Dictionary Should Contain Key` | ${file} | one |
        | `Dictionary Should Contain Key` | ${file} | two | 
        
        *POST Request with Data and File*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{data}= | `Create Dictionary` | name=mallikarjunarao | surname=kosuri |
        | `Create File` | foobar.txt | content=foobar |
        | ${file_data}= | `Get File` | foobar.txt |
        | &{files}= | `Create Dictionary` | file=${file_data} |
        | ${resp}= | `Post Request` | httpbin | /post | files=${files} | data=${data} |
        | `Should Be Equal As Strings` |  ${resp.status_code} | 200 |
        
        *POST Request with URL Params*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{params}= |  `Create Dictionary` |  key=value | key2=value2 |
        | ${resp}= | `Post Request` | httpbin | /post    | params=${params} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |

        *POST Request with JSON Data*
        
        | `Create Session` | httpbin | http://httpbin.org | 
        | &{data}= | `Create Dictionary` |  latitude=30.496346 | longitude=-87.640356 |  
        | ${resp}= | `Post Request` | httpbin | /post | json=${data} | 
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 | 
        | ${jsondata}= | `To Json` | ${resp.content} | 
        | `Should Be Equal` | ${jsondata['json']} | ${data} | 
        
        *POST Request with NO Data*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Post Request` | httpbin | /post | 
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
               
        *POST Request With No Dictionary*
        
        | `Set Test Variable` | ${data} | some content |
        | ${resp}= | `Post Request` | httpbin | /post | data=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | `Should Contain` | ${resp.text} | ${data} |
        
        *POST Request with Unicode Data*
        
        | `Create Session` | httpbin | http://httpbin.org | debug=3 |
        | &{data}= | `Create Dictionary` | name=åº¦å�‡æ�‘ |
        | &{headers}= | `Create Dictionary` | Content-Type=application/x-www-form-urlencoded |
        | ${resp}= | `Post Request` | httpbin | /post | data=${data} | headers=${headers} |
        | `Dictionary Should Contain Value` | ${resp.json()['form']} | åº¦å�‡æ�‘ |
        
        *POST Request with Binary Data in Dictionary*
        
        | `Create Session` | httpbin | http://httpbin.org | debug=3 |
        | ${file_data}= | `Get Binary File` | ${CURDIR}${/}data.json |
        | &{data}= | `Create Dictionary` | name=${file_data.strip()} |
        | &{headers}= | `Create Dictionary` | Content-Type=application/x-www-form-urlencoded |
        | ${resp}= | `Post Request` | httpbin | /post | data=${data} | headers=${headers} |
        | `Log` | ${resp.json()['form']} |
        | `Should Contain` | ${resp.json()['form']['name']} | \u5ea6\u5047\u6751 |
        
        *POST Request with Binary Data*
        
        | `Create Session` | httpbin | http://httpbin.org | debug=3 |
        | ${data}= | `Get Binary File` | ${CURDIR}${/}data.json |
        | &{headers}= | `Create Dictionary` | Content-Type=application/x-www-form-urlencoded |
        | ${resp}= | `Post Request` | httpbin | /post | data=${data} | headers=${headers} |
        | `Log` | ${resp.json()['form']} |
        | ${value}= | `evaluate` | list(${resp.json()}['form'].keys())[0] |
        | `Should Contain` | ${value} | åº¦å�‡æ�‘ |
        
        *POST Request with Arbitrary Binary Data*
        
        | `Create Session` | httpbin | http://httpbin.org | debug=3 | 
        | ${data}= | `Get Binary File` | ${CURDIR}${/}randombytes.bin | 
        | &{headers}= | `Create Dictionary` | Content-Type=application/octet-stream |  Accept=application/octet-stream | 
        | ${resp}= | `Post Request` | httpbin | /post | data=${data} | headers=&{headers} | 
        | # TODO Compare binaries. Content is json with base64 encoded data | 
        | `Log` | "Success" |
        
        *POST request with Redirection*
        
        | `Create Session` | jigsaw | http://jigsaw.w3.org |
        | ${resp}= | `Post Request` | jigsaw | /HTTP/300/302.html |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${resp}= | `Post Request` | jigsaw | /HTTP/300/302.html | allow_redirects=${true} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *POST request without Redirection*
        
        | `Create Session` | jigsaw | http://jigsaw.w3.org | debug=3 |
        | ${resp}= | `Post Request` | jigsaw | /HTTP/300/302.html | allow_redirects=${false} |
        | ${status}= | `Convert To String` | ${resp.status_code} |
        | `Should Start With` | ${status} | 30 |
        
        *PUT Request*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{data}= | `Create Dictionary` | name=bulkan | surname=evcimen |
        | &{headers}= | `Create Dictionary` | Content-Type=application/x-www-form-urlencoded | 
        | ${resp}= | `Put Request` | httpbin | /put | data=${data} | headers=${headers} |
        | `Dictionary Should Contain Value` | ${resp.json()['form']} | bulkan |
        | `Dictionary Should Contain Value` | ${resp.json()['form']} | evcimen |
        
        *PUT Request with URL Params*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{params}= |  `Create Dictionary` |  key=value | key2=value2 |
        | ${resp}= | `Put Request` | httpbin | /put | params=${params} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
                
        *PUT Request with JSON Data *
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{data}= | `Create Dictionary` | latitude=30.496346 | longitude=-87.640356 |
        | ${resp}= | `Put Request` | httpbin | /put | json=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${jsondata}= | `To Json` | ${resp.content} |
        | `Should Be Equal` |  ${jsondata['json']} | ${data} |
        
        *PUT Request with No Dictionary*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | `Set Test Variable` | ${data} | some content |
        | ${resp}= | `Put Request` | httpbin | /put | data=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | `Should Contain` | ${resp.text} | ${data} |
        
        *PUT Request with NO Data*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Put Request` | httpbin | /put |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *PUT request with Redirection*
        
        | `Create Session` | jigsaw | http://jigsaw.w3.org | debug=3 |
        | ${resp}= | `Put Request` | jigsaw | /HTTP/300/302.html |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${resp}= | `Put Request` | jigsaw | /HTTP/300/302.html | allow_redirects=${true} | 
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *PUT request without Redirection*
        
        | `Create Session` | jigsaw | http://jigsaw.w3.org |
        | ${resp}= | `Put Request` | jigsaw | /HTTP/300/302.html | allow_redirects=${false} |
        | ${status}= | `Convert To String` | ${resp.status_code} |
        | `Should Start With` | ${status} | 30 |
        
        *HEAD Request*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Head Request` | httpbin | /headers |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *HEAD request with Redirection*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Head Request` | httpbin | /redirect/1 | allow_redirects=${true} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *HEAD request without Redirection*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Head Request` | httpbin | /redirect/1 |
        | ${status}= | `Convert To String` | ${resp.status_code} |
        | `Should Start With` | ${status} | 30 |
        | ${resp}= | `Head Request` | httpbin | /redirect/1 | allow_redirects=${false} |
        | ${status}= | `Convert To String` | ${resp.status_code} |
        | `Should Start With` | ${status} | 30 |
        
        *OPTIONS Request*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Options Request` | httpbin | /headers |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | `Dictionary Should Contain Key` | ${resp.headers} | allow |
        
        *OPTIONS request with Redirection*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Options Request` | httpbin | /redirect/1 |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${resp}= | `Options Request` | httpbin | /redirect/1 | allow_redirects=${true} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |  
        
        *DELETE Request with URL Params*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{params}= |  `Create Dictionary` |  key=value | key2=value2 |
        | ${resp}= | `Delete Request` | httpbin | /delete    | ${params} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *DELETE Request with NO data*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | ${resp}= | `Delete Request` | httpbin | /delete |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        
        *DELETE Request with Data*
        
        | `Create Session` | httpbin | http://httpbin.org | debug=3 |
        | &{data}= | `Create Dictionary` | name=bulkan | surname=evcimen |
        | ${resp}= | `Delete Request` | httpbin | /delete | data=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | `Log` | ${resp.content} |
        | Comment | `Dictionary Should Contain Value` | ${resp.json()['data']} | bulkan |
        | Comment | `Dictionary Should Contain Value` | ${resp.json()['data']} | evcimen |
        
        *DELETE Request with JSON Data*
        
        | `Create Session` | httpbin | http://httpbin.org |
        | &{data}= | `Create Dictionary` |  latitude=30.496346 | longitude=-87.640356 |
        | ${resp}= | `Delete Request` | httpbin | /delete | json=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${jsondata}= | `To Json` | ${resp.content} |
        | `Should Be Equal` | ${jsondata['json']} | ${data} |
        
        *PATCH Requests*
        
        | `Create Session`  |  httpbin  |  http://httpbin.org |
        | &{data}=  |  `Create Dictionary`  |  name=bulkan  |  surname=evcimen |
        | &{headers}=  |  `Create Dictionary`  |  Content-Type=application/x-www-form-urlencoded |
        | ${resp}=  |  `Patch Request`  |  httpbin  |  /patch  |  data=${data}  |  headers=${headers} |
        | `Dictionary Should Contain Value`  |  ${resp.json()['form']}  |  bulkan |
        | `Dictionary Should Contain Value`  |  ${resp.json()['form']}  |  evcimen |
        
        *PATCH Requests with JSON Data*
        
        | `Create Session` | httpbin  |   http://httpbin.org |
        | &{data}=  |  `Create Dictionary` |  latitude=30.496346 | longitude=-87.640356 |
        | ${resp}=  |   `Patch Request` | httpbin | /patch  |  json=${data} |
        | `Should Be Equal As Strings` | ${resp.status_code} | 200 |
        | ${jsondata}= | `To Json` | ${resp.content} |
        | `Should Be Equal`  |   ${jsondata['json']}  |   ${data} | 
 
        *Pretty Print JSON Object*
        
        | `Log`  |  ${resp} |
        | ${output}=  |  `To Json`  |  ${resp.content}  |  pretty_print=True |
        | `Log`  |  ${output} |
        | `Should Contain`  |  ${output}  |  "key_one": "true" |
        | `Should Contain`  |  ${output}  |  "key_two": "this is a test string" |
        | `Should Not Contain`  |  ${output}  |  {u'key_two': u'this is a test string', u'key_one': u'true'} |

    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = __version__



