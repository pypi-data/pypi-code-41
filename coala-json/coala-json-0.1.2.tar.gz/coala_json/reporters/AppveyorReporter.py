import os
import requests

from coala_json.reporters.ResultReporter import ResultReporter


class AppveyorReporter(ResultReporter):
    """
    Contain methods to report test results to appveyor
    """

    def to_output(self):
        file_to_upload = self.coala_json.split(' ')[0]
        appveyor_job_id = os.getenv('APPVEYOR_JOB_ID')
        appveyor_build_folder = os.getenv('APPVEYOR_BUILD_FOLDER')
        try:
            with open('{}/{}'.format(appveyor_build_folder, file_to_upload),
                      'rb') as f:
                r = requests.post('https://ci.appveyor.com/api/testresults/'
                                  'junit/{}'.format(appveyor_job_id),
                                  files={'{}'.format(file_to_upload): f})
            return r.url
        except (FileNotFoundError, TypeError):
            return 'Permission denied or no such file or directory'
