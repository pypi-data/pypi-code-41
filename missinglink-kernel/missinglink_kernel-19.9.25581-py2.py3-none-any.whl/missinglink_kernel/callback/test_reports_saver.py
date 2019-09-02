import datetime
import json
import tempfile
import uuid

import six


class ReportsSaver(object):
    _TEST_REPORT_BUFFER = 10000

    def __init__(self, experiment_id, experiment_token, project_token, context, logger):
        self._experiment_id = experiment_id
        self._experiment_token = experiment_token
        self._project_token = project_token
        self._context = context
        self.logger = logger
        self._pending_test_report_data_points = 0
        self._json_test_report_file = None
        self._test_report_files = []
        self._test_report_upload_failed = False

    def set_test_token(self, test_token):
        self._test_token = test_token

    @classmethod
    def try_enable_test_report(cls, ctx, project_token):
        from missinglink.core import ApiCaller
        from missinglink.core.api import default_api_retry
        result = ApiCaller.call(ctx.obj.config, ctx.obj.session, 'get', 'test_reports/flag/{project_token}'.format(
            project_token=project_token), retry=default_api_retry())
        return result['value']

    def log_test_report(self, expected, predictions, probabilities, points_metadata, class_mapping):
        if self._test_report_upload_failed:
            return

        if len(expected) != len(predictions) or len(expected) != len(probabilities) or len(expected) != len(points_metadata):
            self.logger.warning("Can't save test report data, some points don't have all the data")
            return

        if self._pending_test_report_data_points == 0:
            self._json_test_report_file = tempfile.TemporaryFile('wb+')

        data = self._generate_test_report_points(expected, predictions, probabilities, points_metadata, class_mapping)
        self._pending_test_report_data_points += len(expected)

        self._json_test_report_file.writelines(six.ensure_binary(json.dumps(item) + '\n') for item in data)

        if self._pending_test_report_data_points >= self._TEST_REPORT_BUFFER:
            self._send_report_data()

    def _send_report_data(self):
        self._pending_test_report_data_points = 0

        file_type = 'json'
        data_object_name = '%s/temp/%s/%s_%s.%s' % (self._project_token, self._experiment_id, 'test_report', uuid.uuid4().hex, file_type)

        content_types = {
            'json': 'application/json'
        }

        default_mime_type = 'application/octet-stream'
        headers = {'Content-Type': content_types.get(file_type, default_mime_type)}

        try:
            put_url = self._get_temp_secure_url(data_object_name, headers)
            from missinglink.legit.gcs_utils import Uploader
            Uploader.upload_http(put_url, None, self._json_test_report_file, headers)
            self._json_test_report_file.close()
            self._test_report_files.append('gs://' + data_object_name)
        except Exception:
            self._test_report_upload_failed = True
            self.logger.exception('Failed to send test report data')

    def _get_temp_secure_url(self, data_object_name, headers):
        self.logger.debug('temp url for %s', data_object_name)

        msg = {
            'path': data_object_name,
            'content_type': headers.get('Content-Type'),
            'token': self._experiment_token,
            'project_token': self._project_token
        }

        from missinglink.core import ApiCaller
        from missinglink.core.api import default_api_retry
        result = ApiCaller.call(self._context.obj.config, self._context.obj.session, 'post', 'test_reports/url', data=msg, retry=default_api_retry())

        return result['url']

    def _generate_test_report_points(self, expected, predictions, probabilities, points_metadata, class_mapping):
        inference_time = datetime.datetime.utcnow().isoformat()
        for (exp, pred, prob, points_info) in zip(expected, predictions, probabilities, points_metadata):
            for point_info in points_info or []:
                data = {
                    'experiment_id': self._experiment_id,
                    'test_token': self._test_token,
                    'expected': exp,
                    'predicted': pred,
                    'probabilities': [float(v) for v in prob],
                    'datetime': inference_time
                }
                if class_mapping:
                    data['class_mapping'] = [{'class_id': cl_id, 'class_name': cl_name} for cl_id, cl_name in class_mapping.items()]
                data.update(point_info)
                yield data

    def test_end(self):
        if self._pending_test_report_data_points > 0:
            self._send_report_data()

        if len(self._test_report_files) > 0 and not self._test_report_upload_failed:
            self.save_test_report_urls()

    def save_test_report_urls(self):
        self.logger.debug('add data %s', self._test_report_files)

        try:
            msg = {
                'token': self._experiment_token,
                'test_token': self._test_token,
                'report_urls': self._test_report_files,
                'project_token': self._project_token
            }
            from missinglink.core import ApiCaller
            from missinglink.core.api import default_api_retry
            ApiCaller.call(self._context.obj.config, self._context.obj.session, 'post', 'test_reports/save', data=msg, retry=default_api_retry())
        except Exception:
            self.logger.exception('Failed to save test report data')
