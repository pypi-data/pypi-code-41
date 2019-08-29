#   Copyright 2019 Intentionet
#
#   Licensed under the proprietary License included with this package;
#   you may not use this file except in compliance with the License.
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
"""Test Asserts class."""
import pytest
import six
from pandas import DataFrame
from pybatfish.exception import BatfishAssertException

from pybfe.client.session import (Asserts)
from pybfe.datamodel.policy import (STATUS_ERROR, STATUS_FAIL, STATUS_PASS)
from tests.common_util import (MockQuestion, MockSession, MockTableAnswer)

if six.PY3:
    from unittest.mock import patch
else:
    from mock import patch

ERROR_MESSAGE = 'error message'


@pytest.fixture()
def session():
    return MockSession()


@pytest.fixture()
def asserts(session):
    return Asserts(session)


@pytest.fixture()
def session_with_metadata():
    return MockSession(assert_name='assert', test_name='test',
                       policy_name='policy', policy_id='pid')


@pytest.fixture()
def asserts_with_metadata(session_with_metadata):
    return Asserts(session_with_metadata)


@pytest.mark.parametrize('assert_func, params, helper', [
    ('assert_filter_denies',
     {
         'filters': 'filters',
         'headers': 'headers',
         'startLocation': 'startLocation',
     },
     "pybfe.client.session.assert_filter_denies"
     ),
    ('assert_filter_has_no_unreachable_lines',
     {
         'filters': 'filters',
     },
     "pybfe.client.session.assert_filter_has_no_unreachable_lines"
     ),
    ('assert_filter_permits',
     {
         'filters': 'filters',
         'headers': 'headers',
         'startLocation': 'startLocation',
     },
     "pybfe.client.session.assert_filter_permits",
     ),
    ('assert_flows_fail',
     {
         'startLocation': 'startLocation',
         'headers': 'headers',
     },
     "pybfe.client.session.assert_flows_fail"
     ),
    ('assert_flows_succeed',
     {
         'startLocation': 'startLocation',
         'headers': 'headers',
     },
     "pybfe.client.session.assert_flows_succeed"
     ),
    ('assert_no_forwarding_loops',
     {},
     "pybfe.client.session.assert_no_forwarding_loops"
     ),
    ('assert_no_incompatible_bgp_sessions',
     {
         'nodes': 'nodes',
         'remote_nodes': 'remote_nodes',
         'status': 'status',
     },
     "pybfe.client.session.assert_no_incompatible_bgp_sessions"
     ),
    ('assert_no_unestablished_bgp_sessions',
     {
         'nodes': 'nodes',
         'remote_nodes': 'remote_nodes',
     },
     "pybfe.client.session.assert_no_unestablished_bgp_sessions"
     ),
    ('assert_no_undefined_references',
     {},
     "pybfe.client.session.assert_no_undefined_references"
     ),
    ('assert_vtep_reachability',
     {},
     "pybfe.client.session.Asserts._assert_vtep_reachability_helper"
     ),
])
def test_asserts(asserts, assert_func, params, helper):
    """Test that each assert records the expected result with passing, failing, and error conditions."""
    record_target = 'pybfe.client.session.Asserts._record_result'
    with patch(helper) as mock_assert, patch(
            record_target) as mock_record_result:
        # Passing assert should trigger recording passing result
        mock_assert.return_value = "result"
        getattr(asserts, assert_func)(snapshot='ss1', **params)
        mock_record_result.assert_called_with(snapshot='ss1', result='result',
                                              status=STATUS_PASS,
                                              message='Assertion passed!')

        # Forcing a BatfishAssertException should trigger recording failed result
        mock_assert.side_effect = BatfishAssertException(ERROR_MESSAGE)
        with pytest.raises(BatfishAssertException):
            getattr(asserts, assert_func)(snapshot='ss1', **params)
        mock_record_result.assert_called_with(snapshot='ss1',
                                              result=ERROR_MESSAGE,
                                              status=STATUS_FAIL)

        # Forcing another exception should trigger recording errored result
        mock_assert.side_effect = ValueError(ERROR_MESSAGE)
        with pytest.raises(ValueError):
            getattr(asserts, assert_func)(snapshot='ss1', **params)
        mock_record_result.assert_called_with(snapshot='ss1',
                                              result=ERROR_MESSAGE,
                                              status=STATUS_ERROR)


def test_record_result(asserts_with_metadata):
    """Confirm recording an assertion result correctly triggers adding a new assertion to the current Policy."""
    with patch.object(asserts_with_metadata.session,
                      '_add_assertion') as mock_add:
        asserts_with_metadata._record_result(result='result', status='status',
                                             message='message', snapshot='ss1')
        mock_add.assert_called_with(policy_name='policy', policy_id='pid',
                                    test_name='test', assert_name='assert',
                                    status='status', message='message',
                                    snapshot='ss1')


def test_record_result_no_policy(asserts):
    """Confirm recording an assertion result is a noop when there is no Policy specified."""
    with patch.object(asserts.session, '_add_assertion') as mock_add:
        asserts._record_result(result='result', status='status',
                               message='message')
        assert not mock_add.called


def test_vtep_reachability_helper(session):
    """Confirm vtep-reachability helper passes and fails as expected based on the result."""
    with patch.object(session.q, 'vxlanReachabilityAnalyzer',
                      create=True) as vxlanReachabilityAnalyzer:
        # Test success
        vxlanReachabilityAnalyzer.return_value = MockQuestion()
        session.asserts._assert_vtep_reachability_helper(snapshot=None,
                                                         soft=False,
                                                         df_format="table")
        # Test failure
        mock_df = DataFrame.from_records(
            [{'UnreachableVtep': 'found', 'More': 'data'}])
        vxlanReachabilityAnalyzer.return_value = MockQuestion(
            MockTableAnswer(mock_df))
        with pytest.raises(BatfishAssertException) as excinfo:
            session.asserts._assert_vtep_reachability_helper(snapshot=None,
                                                             soft=False,
                                                             df_format="table")
        # Ensure found answer is printed
        assert mock_df.to_string() in str(excinfo.value)


if __name__ == "__main__":
    pytest.main()
