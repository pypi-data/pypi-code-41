import json
import unittest
import re
from preparation_and_cleaning import *
from ibm_ai_openscale.supporting_classes.enums import ProblemType
tc = unittest.TestCase()


def assert_datamart_details(details, schema, state='active'):
    print("** assert_datamart_details **\nDatamart details: {}".format(details))
    tc.assertIsNotNone(details)
    tc.assertEqual(details['status']['state'], state)
    tc.assertEqual(details['database_configuration']['location']['schema'], schema)


def assert_subscription_details(subscription_details, asset_uid=None, no_deployments=None, text_included="", enabled_monitors=[]):
    print("** assert_subscription_details **\nSubscription details: {}".format(subscription_details))

    for configuration in subscription_details['entity']['configurations']:
        if configuration['type'] in enabled_monitors:
            tc.assertTrue(configuration['enabled'], msg="{} is disabled.".format(configuration['type']))

    if asset_uid is not None:
        tc.assertEqual(asset_uid, subscription_details['entity']['asset']['asset_id'])

    if no_deployments is not None:
        tc.assertEqual(no_deployments, len(subscription_details['entity']['deployments']))

    tc.assertIn(text_included, str(subscription_details))


def assert_payload_logging_configuration(payload_logging_details, dynamic_schema_update=False):
    print("** assert_payload_logging_configuration **\nPayload logging details: {}".format(payload_logging_details))

    tc.assertIsNotNone(payload_logging_details)
    tc.assertTrue(payload_logging_details['enabled'])
    if dynamic_schema_update:
        tc.assertTrue(payload_logging_details['parameters']['dynamic_schema_update'], msg="Dynamic schema update is disabled.")


def assert_performance_monitoring_configuration(performance_monitoring_details):
    print("** assert_performance_monitoring_configuration **\nPerformance monitoring details: {}".format(performance_monitoring_details))

    tc.assertIsNotNone(performance_monitoring_details)
    tc.assertTrue(performance_monitoring_details['enabled'])


def assert_quality_monitoring_configuration(quality_monitoring_details):
    print("** assert_quality_monitoring_configuration **\nQuality monitoring details: {}".format(quality_monitoring_details))

    tc.assertIsNotNone(quality_monitoring_details)
    tc.assertTrue(quality_monitoring_details['enabled'])


def assert_explainability_configuration(explainability_details):
    print("** assert_explainability_configuration **\nExplainability details: {}".format(explainability_details))

    tc.assertIsNotNone(explainability_details)
    tc.assertTrue(explainability_details['enabled'])


def assert_fairness_configuration(fairness_monitoring_details):
    print("** assert_fairness_configuration **\nFariness monitoring details: {}".format(fairness_monitoring_details))

    tc.assertIsNotNone(fairness_monitoring_details)
    tc.assertTrue(fairness_monitoring_details['enabled'])

def assert_fairness_recommended_attributes(recommendations, expected_attribute_list):   
    features =  recommendations['parameters']['features']
    for feature in features:
        tc.assertIn(feature['feature'], expected_attribute_list)

def assert_payload_logging_pandas_table_content(pandas_table_content, scoring_records=None):
    print("** assert_payload_logging_pandas_table_content **\nPayload pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape
    payload_error_table = None

    if scoring_records is not None and rows != scoring_records:
        if is_postgres_database():
            query_rows = print_schema_tables_info(postgres_credentials=get_database_credentials(),
                                                  schema_name=get_schema_name())
            for query_row in query_rows:
                if 'PayloadError' in query_row[2]:
                    payload_error_table = query_row[2]
            if payload_error_table is not None:
                print("Payload error table found: {}\nContent: ".format(payload_error_table))
                print(execute_sql_query(""" SELECT * FROM {}."{}" """.format(get_schema_name(), payload_error_table),
                                        postgres_credentials=get_database_credentials()))
        # else:
        #     tables = list_db2_tables(db2_credentials=get_database_credentials(), schema_name=get_schema_name())
        #     for table in tables:
        #         if 'PayloadError' in str(table):
        #             payload_error_table = str(table)

    tc.assertIsNone(payload_error_table, msg="Payload error table found in schema!")

    if scoring_records is not None:
        tc.assertEqual(scoring_records, rows, msg="Number of scored records ({}) is different than logged in table ({})".format(scoring_records, rows))


def assert_payload_logging_python_table_content(python_table_content, fields=[]):
    print("** assert_payload_logging_python_table_content **\nPayload python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_payload_logging_unstructured_data(subscription, scoring_records=None):
    print("** assert_payload_logging_unstructured_data **\n")

    rows = subscription.payload_logging._get_data_from_rest_api()

    tc.assertGreater(len(rows), 0, msg="Payload logging table is empty!")

    payload_error_table = None
    if scoring_records is not None and rows != scoring_records:
        if "db2" in str(get_database_credentials()):
            pass
        elif "ICP" in get_env():
            pass
        else:
            query_rows = print_schema_tables_info(postgres_credentials=get_database_credentials(), schema_name=get_schema_name())
            for query_row in query_rows:
                if 'PayloadError' in query_row[2]:
                    payload_error_table = query_row[2]
            if payload_error_table is not None:
                print("Payload error table found: {}\nContent: ".format(payload_error_table))
                print(execute_sql_query(""" SELECT * FROM {}."{}" """.format(get_schema_name(), payload_error_table), postgres_credentials=get_database_credentials()))

    if scoring_records is not None:
        tc.assertEqual(scoring_records, len(rows), msg="Number of scored records ({}) is different than logged in table ({})".format(scoring_records, len(rows)))


def assert_performance_monitoring_pandas_table_content(pandas_table_content):
    print("** assert_performance_monitoring_pandas_table_content **\nPerformance pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Performance monitoring table is empty.")


def assert_performance_monitoring_python_table_content(python_table_content, fields=[]):
    print("** assert_performance_monitoring_python_table_content **\nPerformance python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_quality_run(run_details):
    print("** assert_quality_run **\nQuality run details:\n{}".format(run_details))
    tc.assertIn('Prerequisite Check', str(run_details))


def assert_quality_entire_run(subscription, run_details):
    print("** assert_quality_entire_run **\nQuality run details:\n{}".format(run_details))
    tc.assertIn('Prerequisite Check', str(run_details), msg="Quality run start failed: {}".format(run_details))

    status = run_details['status']
    id = run_details['id']
    start_time = time.time()
    elapsed_time = 0

    while status != 'completed' and elapsed_time < get_quality_run_timeout():
        time.sleep(10)
        run_details = subscription.quality_monitoring.get_run_details(run_uid=id)
        status = run_details['status']
        elapsed_time = time.time() - start_time
        tc.assertNotEqual('failed', status, msg="Quality run status failed. Reason: {}".format(run_details))
    print("Final run details: {}".format(run_details))
    tc.assertEqual('completed', status, msg="Quality run is not completed. Latest run details: {}".format(run_details))


def assert_quality_monitoring_pandas_table_content(pandas_table_content):
    print("** assert_quality_monitoring_pandas_table_content **\nQuality pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Quality monitoring table is empty.")


def assert_quality_monitoring_python_table_content(python_table_content, fields=[]):
    print("** assert_quality_monitoring_python_table_content **\nQuality python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_get_quality_metrics(quality_run_details, data_mart_quality_metrics, quality_monitoring_metrics):

    tc.assertEqual(quality_run_details['status'], 'completed', msg="Quality run is not completed. Cannot get metrics")
    tc.assertIsNotNone(data_mart_quality_metrics, msg="Empty quality metrics from data mart")
    tc.assertIsNotNone(quality_monitoring_metrics, msg="Empty quality metrics from quality monitoring")

    metrics = quality_run_details["output"]["metrics"]
    print("\n Quality metrics from DataMart API: \n{}".format(data_mart_quality_metrics))

    for dm_metric in data_mart_quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['metrics']:
        if dm_metric['name'] in metrics.keys():
            tc.assertEqual(dm_metric['value'], metrics[dm_metric['name']],
                           msg="Quality metric {} has different value in data_mart api".format(dm_metric['name']))

    print(" Quality metrics from QualityMonitoring API: \n{}".format(quality_monitoring_metrics))
    for qm_metric in quality_monitoring_metrics[0]['metrics']:
        if qm_metric['id'] in metrics.keys():
            tc.assertEqual(qm_metric['value'], metrics[qm_metric['id']],
                           msg="\n\nQuality metric {} has different value in quality_monitoring api".format(qm_metric['id']))
    print("\nQuality metrics from different APIs are EQUAL: {}".format(metrics))


def assert_quality_metrics_binary_model(quality_metrics, quality_monitoring_details):
    tc.assertIsNotNone(quality_metrics, msg="Empty quality metrics")
    tc.assertEqual(quality_monitoring_details['parameters']['evaluation_definition']['method'], ProblemType.BINARY_CLASSIFICATION,
                   msg="Wrong assert method for the model's problem type")
    calculated_metrics = set()
    for quality_metric in quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['metrics']:
        calculated_metrics.add(quality_metric['name'])
    tc.assertGreater(len(calculated_metrics), 0, msg="Empty calculated quality metrics")

    binary_metrics = set()
    for metric in quality_monitoring_details['monitor_definition']['entity']['metrics']:
        if ProblemType.BINARY_CLASSIFICATION in metric['applies_to']['problem_type']:
            binary_metrics.add(metric['id'])
    if not calculated_metrics == binary_metrics:
        print("{} metrics has been not calculated for the model".format(binary_metrics.difference(calculated_metrics)))
    else:
        print("All quality metrics has been calculated for the model. List of the metrics:\n {}".format(calculated_metrics))


def assert_quality_metrics_multiclass_model(quality_metrics, quality_monitoring_details):
    tc.assertIsNotNone(quality_metrics, msg="Empty quality metrics")
    tc.assertEqual(quality_monitoring_details['parameters']['evaluation_definition']['method'], ProblemType.MULTICLASS_CLASSIFICATION,
                   msg="Wrong assert method for the model's problem type")
    calculated_metrics = set()
    for quality_metric in quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['metrics']:
        calculated_metrics.add(quality_metric['name'])
    tc.assertGreater(len(calculated_metrics), 0, msg="Empty calculated quality metrics")

    multiclass_metrics = set()
    for metric in quality_monitoring_details['monitor_definition']['entity']['metrics']:
        if ProblemType.MULTICLASS_CLASSIFICATION in metric['applies_to']['problem_type']:
            multiclass_metrics.add(metric['id'])
    if not calculated_metrics == multiclass_metrics:
        print("{} metrics has been not calculated for the model".format(multiclass_metrics.difference(calculated_metrics)))
    else:
        print("All quality metrics has been calculated for the model. List of the metrics:\n {}".format(calculated_metrics))


def assert_quality_metrics_regression_model(quality_metrics, quality_monitoring_details):
    tc.assertIsNotNone(quality_metrics, msg="Empty quality metrics")
    tc.assertEqual(quality_monitoring_details['parameters']['evaluation_definition']['method'], ProblemType.REGRESSION,
                   msg="Wrong assert method for the model's problem type")
    calculated_metrics = set()
    for quality_metric in quality_metrics['deployment_metrics'][0]['metrics'][0]['value']['metrics']:
        calculated_metrics.add(quality_metric['name'])
    tc.assertGreater(len(calculated_metrics), 0, msg="Empty calculated quality metrics")

    regression_metrics = set()
    for metric in quality_monitoring_details['monitor_definition']['entity']['metrics']:
        if ProblemType.REGRESSION in metric['applies_to']['problem_type']:
            regression_metrics.add(metric['id'])
    if not calculated_metrics == regression_metrics:
        print("{} metrics has been not calculated for the model".format(regression_metrics.difference(calculated_metrics)))
    else:
        print("All quality metrics has been calculated for the model. List of the metrics:\n{}".format(calculated_metrics))


def assert_explainability_pandas_table_content(pandas_table_content):
    print("** assert_explainability_pandas_table_content **\nExplainability pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Explainability table is empty.")


def assert_explainability_python_table_content(python_table_content, fields=[]):
    print("** assert_explainability_python_table_content **\nExplainability python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_fairness_monitoring_pandas_table_content(pandas_table_content):
    print("** assert_fairness_monitoring_pandas_table_content **\nFairness pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    tc.assertGreater(rows, 0, msg="Fairness monitoring table is empty.")


def assert_fairness_monitoring_python_table_content(python_table_content, fields=[]):
    print("** assert_fairness_monitoring_python_table_content **\nFairness python table content: {}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_feedback_pandas_table_content(pandas_table_content, feedback_records=None):
    print("** assert_feedback_pandas_table_content **\nFeedback pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    if feedback_records is not None:
        tc.assertEqual(feedback_records, rows, msg="Number of records send to feedback ({}) is different than logged in table ({})".format(feedback_records, rows))


def assert_feedback_python_table_content(python_table_content, fields=[]):
    print("** assert_feedback_python_table_content **\nFeedback python table content:{}".format(python_table_content))

    tc.assertIsNotNone(python_table_content)

    for field in fields:
        tc.assertIn(field, python_table_content['fields'])


def assert_feedback_logging_unstructured_data(subscription, feedback_records=None):
    print("** assert_payload_logging_unstructured_data **\n")

    rows = subscription.feedback_logging._get_data_from_rest_api()

    tc.assertGreater(len(rows), 0, msg="Feedback logging table is empty!")

    if feedback_records is not None:
        tc.assertEqual(feedback_records, len(rows), msg="Number of scored records ({}) is different than logged in table ({})".format(feedback_records, len(rows)))


def assert_metrics_pandas_table_content(pandas_table_content, metrics_records=None):
    print("** assert_metrics_pandas_table_content **\nMetrics pandas table content:\n{}".format(pandas_table_content))
    rows, columns = pandas_table_content.shape

    if metrics_records is not None:
        tc.assertEqual(metrics_records, rows)


def assert_metrics_python_table_content(python_table_content, metrics=[], metrics_values=[]):
    print("** assert_metrics_python_table_content **\nMetrics python table content:\n{}".format(python_table_content))
    tc.assertIsNotNone(python_table_content)

    for metric in metrics:
        tc.assertIn(str(metric), str(python_table_content))

    for metric_value in metrics_values:
        tc.assertIn(str(metric_value), str(python_table_content))


def assert_metric(metrics_content, metric_json, binding_id, monitor_definition_id):
    print("** assert_metric **\nMetrics content:\n{}".format(metrics_content))
    tc.assertIsNotNone(metrics_content)

    metric_exists = False
    for monitor in metrics_content:
        for metric in monitor['metrics']:
            if metric_json == metric:
                metric_exists = True
                break

        tc.assertEqual(binding_id, monitor['binding_id'])
        tc.assertEqual(monitor_definition_id, monitor['monitor_definition_id'])

    tc.assertTrue(metric_exists, msg="Provided metric {} does not exist in metrics content!")


def assert_custom_monitor_enablement(subscription_details, monitor_uid, enabled=True):
    print("** assert_custom_monitor_enablement **\nSubscription details:\n{}".format(subscription_details))
    for configuration in subscription_details['entity']['configurations']:
        if configuration['monitor_definition_id'] == monitor_uid:
            tc.assertEqual(configuration['enabled'], enabled)


def assert_monitors_enablement(subscription_details, payload=False, performance=False, quality=False, fairness=False, explainability=False):
    print("** assert_monitors_enablement **\nSubscription details: {}".format(subscription_details))

    for configuration in subscription_details['entity']['configurations']:
        if configuration['type'] == 'payload_logging':
            tc.assertEqual(payload, configuration['enabled'], msg="Payload logging is {}. Assert expectation: {}".format(configuration['enabled'], payload))
        elif configuration['type'] == 'performance_monitoring':
            tc.assertEqual(performance, configuration['enabled'], msg="Performance monitoring is {}. Assert expectation: {}".format(configuration['enabled'], performance))
        elif configuration['type'] == 'quality_monitoring':
            tc.assertEqual(quality, configuration['enabled'], msg="Quality monitoring is {}. Assert expectation: {}".format(configuration['enabled'], quality))
        elif configuration['type'] == 'fairness_monitoring':
            tc.assertEqual(fairness, configuration['enabled'], msg="Fairness monitoring is {}. Assert expectation: {}".format(configuration['enabled'], fairness))
        elif configuration['type'] == 'explainability':
            tc.assertEqual(explainability, configuration['enabled'], msg="Explainability is {}. Assert expectation: {}".format(configuration['enabled'], explainability))


def assert_explainability_run(explainability_run_details):
    print("** assert_explainability_run **\nExplainability run details: {}".format(explainability_run_details))

    tc.assertIsNotNone(explainability_run_details)
    statuses = explainability_run_details['entity']['status']

    for status in statuses.values():
        if status == 'not_supported':
            break
        tc.assertEqual("finished", status, msg="Explainability run failed in single step.")


def assert_explainability_not_supported_run(explainability_run_details):
    print("** assert_explainability_not_supported_run **\nExplainability run details: {}".format(explainability_run_details))

    tc.assertIsNotNone(explainability_run_details)
    statuses = explainability_run_details['entity']['status']

    for status in statuses.values():
        tc.assertEqual("not_supported", status, msg="Explainability failed but should be not supported.")


def assert_fairness_run(fairness_run_details):
    print("** assert_fairness_run **\nFairness run details: {}".format(fairness_run_details))

    tc.assertIsNotNone(fairness_run_details)
    tc.assertEqual('FINISHED', fairness_run_details['entity']['parameters']['last_run_status'])

    tc.assertTrue(bool(re.match("(.*Copied the previous fairness metrics as there are no new runtime.*|.*bias run is successful.*)", str(fairness_run_details))))


def assert_performance_metrics(metrics):
    print("** assert_performance_metrics **\nPerformance metrics: {}".format(metrics))
    tc.assertGreater(len(metrics['metrics']), 0, msg="Performance metrics are empty.")


def assert_deployment_metrics(metrics):
    print("** assert_deployment_metrics **\nDeployment metrics: {}".format(metrics))
    tc.assertGreater(len(metrics['deployment_metrics']), 0, msg="Deployment metrics are empty.")


def skip_on_sanity_run():
    if "E2E_SANITY" in get_env():
        tc.skipTest("Only quality monitoring should be tested on that environment.")