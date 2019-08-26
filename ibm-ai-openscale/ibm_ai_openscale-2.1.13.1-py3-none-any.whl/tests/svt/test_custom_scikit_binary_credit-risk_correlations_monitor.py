# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from assertions import *
import pandas as pd
from ibm_ai_openscale.supporting_classes.payload_record import PayloadRecord
from ibm_ai_openscale.utils.href_definitions_v2 import AIHrefDefinitionsV2
from ibm_ai_openscale.utils.inject_historical_data import load_historical_kpi_measurement, load_historical_payload, load_historical_drift_measurement


DAYS = 7


class TestAIOpenScaleClient(unittest.TestCase):
    hrefs_v2 = None
    log_loss_random = None
    brier_score_loss = None
    application_instance_id = None
    drift_instance_id = None
    data_set_id = None
    ai_client = None
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    b_app_uid = None
    x_uid = None
    labels = None
    corr_monitor_instance_id = None
    variables = None
    wml_client = None
    subscription = None
    binding_uid = None
    aios_model_uid = None
    scoring_result = None
    payload_scoring = None
    published_model_details = None
    monitor_uid = None
    source_uid = None
    correlation_monitor_uid = 'correlations'
    measurement_details = None
    transaction_id = None
    drift_model_name = "drift_detection_model.tar.gz"
    drift_model_path = os.path.join(os.getcwd(), 'artifacts', 'drift_models')
    data_df = pd.read_csv(
        "./datasets/German_credit_risk/credit_risk_training.csv",
        dtype={'LoanDuration': int, 'LoanAmount': int, 'InstallmentPercent': int, 'CurrentResidenceDuration': int,
               'Age': int, 'ExistingCreditsCount': int, 'Dependents': int})

    test_uid = str(uuid.uuid4())

    # Custom deployment configuration
    credentials = {
        "url": "http://169.63.194.147:31520",
        "username": "xxx",
        "password": "yyy",
        "request_headers": {"content-type": "application/json"}
    }

    def score(self, subscription_details):
        fields = ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount", "ExistingSavings",
                  "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan", "CurrentResidenceDuration",
                  "OwnsProperty", "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount", "Job", "Dependents",
                  "Telephone", "ForeignWorker"]
        values = [
            ["no_checking", 13, "credits_paid_to_date", "car_new", 1343, "100_to_500", "1_to_4", 2, "female", "none", 3,
             "savings_insurance", 25, "none", "own", 2, "skilled", 1, "none", "yes"],
            ["no_checking", 24, "prior_payments_delayed", "furniture", 4567, "500_to_1000", "1_to_4", 4, "male", "none",
             4, "savings_insurance", 60, "none", "free", 2, "management_self-employed", 1, "none", "yes"]
        ]

        payload = {"fields": fields, "values": values}
        header = {'Content-Type': 'application/json', 'Authorization': 'Bearer xxx'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)

        return payload, response.json(), 25

    @classmethod
    def setUpClass(cls):
        try:
            requests.get(url="{}/v1/deployments".format(cls.credentials['url']), timeout=10)
        except:
            raise unittest.SkipTest("Custom app is not available.")

        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.hrefs_v2 = AIHrefDefinitionsV2(cls.aios_credentials)
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        self.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_02_bind_custom(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("My Custom deployment", CustomMachineLearningInstance(self.credentials))
        print("Binding uid: {}".format(self.binding_uid))
        self.assertIsNotNone(self.binding_uid)

    def test_03_get_binding_details(self):
        binding_details = self.ai_client.data_mart.bindings.get_details()
        print("Binding details: {}".format(binding_details))
        self.assertIsNotNone(binding_details)

    def test_04_get_deployments(self):
        print('Available deployments: {}'.format(self.ai_client.data_mart.bindings.get_asset_deployment_details()))
        self.ai_client.data_mart.bindings.list_assets()
        self.ai_client.data_mart.bindings.get_asset_details()

    def test_05_subscribe_custom(self):
        subscription = self.ai_client.data_mart.subscriptions.add(
            CustomMachineLearningAsset(
                source_uid='credit',
                label_column='Risk',
                prediction_column='prediction',
                probability_column='probability',
                feature_columns=['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                                 'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex', 'OthersOnLoan',
                                 'CurrentResidenceDuration', 'OwnsProperty', 'Age', 'InstallmentPlans', 'Housing',
                                 'ExistingCreditsCount', 'Job', 'Dependents', 'Telephone', 'ForeignWorker'],
                categorical_columns=['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                     'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty', 'InstallmentPlans',
                                     'Housing', 'Job', 'Telephone', 'ForeignWorker'],
                binding_uid=self.binding_uid))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print('Subscription details: ', subscription.get_details())
        print("Subscription id: {}".format(self.subscription_uid))
        self.assertIsNotNone(self.subscription_uid)

    def test_06_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)
        self.assertIsNotNone(self.subscription)

    def test_07_score_model_and_log_payload(self):
        request, response, response_time = self.score(self.subscription.get_details())
        print('response: ' + str(response))

        records_list = []

        for i in range(0, 5):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription.payload_logging.store(records=records_list)

    def test_08_stats_on_payload_logging_table(self):
        wait_for_payload_table(subscription=self.subscription, payload_records=10)
        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content,
                                                    scoring_records=10)

        print('subscription details', TestAIOpenScaleClient.subscription.get_details())

    def test_09_define_business_app(self):
        payload = {
            "name": "Credit Risk Application",
            "description": "Test Business Application",
            "payload_fields": [
                {
                    "name": "LoanDuration",
                    "type": "number",
                    "description": "kokoko"
                },
                {
                    "name": "LoanPurpose",
                    "type": "string",
                    "description": "kokoko"
                },
                {
                    "name": "LoanAmount",
                    "type": "number",
                    "description": "kokoko"
                },
                {
                    "name": "InstallmentPercent",
                    "type": "number",
                    "description": "kokoko"
                },
                {
                    "name": "RiskPercent",
                    "type": "number",
                    "description": "kokoko"
                }
            ],
            "business_metrics": [
                {
                    "name": "Number Accepted",
                    "description": "string",
                    "expected_direction": "increasing",
                    "thresholds": [
                        {
                            "type": "lower_limit",
                            "default": 0,
                            "default_recommendation": "string"
                        }
                    ],
                    "required": False,
                    "calculation_metadata": {
                        "field_name": "LoanDuration",
                        "aggregation": "avg",
                        "time_frame": {
                            "count": 7,
                            "unit": "day"
                        }
                    }
                },
                {
                    "name": "Monthly Revenue",
                    "description": "string",
                    "expected_direction": "increasing",
                    "thresholds": [
                        {
                            "type": "lower_limit",
                            "default": 0,
                            "default_recommendation": "string"
                        }
                    ],
                    "required": False,
                    "calculation_metadata": {
                        "field_name": "LoanDuration",
                        "aggregation": "avg",
                        "time_frame": {
                            "count": 7,
                            "unit": "day"
                        }
                    }
                }
            ],
            "subscription_ids": [
                TestAIOpenScaleClient.subscription_uid
            ],
        }

        response = requests.post(url=self.hrefs_v2.get_applications_href(),
                                 headers=TestAIOpenScaleClient.ai_client._get_headers(), json=payload)
        print(response.status_code, response.json())
        self.assertEqual(response.status_code, 202)
        TestAIOpenScaleClient.b_app_uid = response.json()['metadata']['id']
        self.assertIsNotNone(TestAIOpenScaleClient.b_app_uid)

    def test_10_get_application_details(self):
        response = requests.get(url=self.hrefs_v2.get_application_details_href(TestAIOpenScaleClient.b_app_uid),
                                 headers=TestAIOpenScaleClient.ai_client._get_headers())
        self.assertEqual(response.status_code, 200)
        print(response.status_code, response.json())

    def test_11_enable_drift(self):
        self.subscription.drift_monitoring.enable(threshold=0.6, min_records=10, model_path=os.path.join(self.drift_model_path, self.drift_model_name))
        drift_monitor_details = self.subscription.monitoring.get_details(monitor_uid='drift')
        print('drift monitor details', drift_monitor_details)

    def test_12_list_monitors_instances(self):
        self.ai_client.data_mart.monitors.list()
        response = requests.get(url=self.hrefs_v2.get_monitor_instances_href(), headers=self.ai_client._get_headers())
        print(response.json())
        instances = response.json()['monitor_instances']

        for instance in instances:
            if 'managed_by' in instance['entity'] and instance['entity']['managed_by'] == self.b_app_uid:
                TestAIOpenScaleClient.application_instance_id = instance['metadata']['id']

            if instance['entity']['monitor_definition_id'] == 'correlations':
                TestAIOpenScaleClient.corr_monitor_instance_id = instance['metadata']['id']

            if instance['entity']['monitor_definition_id'] == 'drift':
                TestAIOpenScaleClient.drift_instance_id = instance['metadata']['id']

        self.assertIsNotNone(TestAIOpenScaleClient.application_instance_id)
        self.assertIsNotNone(TestAIOpenScaleClient.corr_monitor_instance_id)
        self.assertIsNotNone(TestAIOpenScaleClient.drift_instance_id)
        print('application_instance_id', self.application_instance_id)
        print('corr_monitor_instance_id', self.corr_monitor_instance_id)
        print('drift_instance_id', self.drift_instance_id)

    def test_13_load_historical_bkpis(self):
        file_path = os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'historical_records', 'history_kpi.json')

        load_historical_kpi_measurement(
            file_path=file_path,
            aios_credentials=self.aios_credentials,
            monitor_instance_id=self.application_instance_id,
            business_application_id=self.b_app_uid,
            days=DAYS
        )

        load_historical_kpi_measurement(
            file_path=file_path,
            aios_credentials=self.aios_credentials,
            monitor_instance_id=self.application_instance_id,
            business_application_id=self.b_app_uid,
            days=2,
            batch_id_start=500
        )

        load_historical_kpi_measurement(
            file_path=file_path,
            aios_credentials=self.aios_credentials,
            monitor_instance_id=self.application_instance_id,
            business_application_id=self.b_app_uid,
            days=2,
            batch_id_start=1000,
            ignore_metrics=['number_accepted']
        )

    def test_13b_get_historical_kpi(self):
        query = '?start=2018-01-23T12:46:55.677590Z&end=2019-12-04T12:46:55.677590Z&limit=1000'
        metrics_url = self.hrefs_v2.get_measurements_href(self.application_instance_id) + query
        response = requests.get(url=metrics_url, headers=self.ai_client._get_headers())

        self.assertEqual(200, response.status_code)
        print(response.json())
        print(response.json()['measurements'][0])

    def test_14_define_business_payload(self):
        payload = {
            "data_mart_id": self.aios_credentials['instance_guid'],
            "name": "Test application data set",
            "description": "Credit risk business payload",
            "type": "business_payload",
            "target": {
                "target_type": "business_application",
                "target_id": TestAIOpenScaleClient.b_app_uid
            },
            "data_schema": {
                "type": "struct",
                "fields": [
                    {
                        "name": "LoanDuration",
                        "type": "integer",
                        "nullable": False
                    },
                    {
                        "name": "LoanPurpose",
                        "type": "string",
                        "nullable": False
                    },
                    {
                        "name": "LoanAmount",
                        "type": "integer",
                        "nullable": False
                    },
                    {
                        "name": "InstallmentPercent",
                        "type": "integer",
                        "nullable": False
                    },
                    {
                        "name": "RiskPercent",
                        "type": "double",
                        "nullable": False
                    }
                ]
            }
        }

        response = requests.post(url=self.hrefs_v2.get_data_sets_href(), headers=self.ai_client._get_headers(), json=payload)
        self.assertEqual(response.status_code, 202)
        TestAIOpenScaleClient.data_set_id = response.json()['metadata']['id']
        self.assertIsNotNone(TestAIOpenScaleClient.data_set_id)
        print(response.json())

    def test_15_get_data_set_details(self):
        response = requests.get(url=self.hrefs_v2.get_data_set_details_href(TestAIOpenScaleClient.data_set_id), headers=self.ai_client._get_headers())
        self.assertEqual(response.status_code, 200)
        print(response.json())

    def test_16_insert_business_payload(self):
        file_path = os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'historical_records', 'history_business_payload.json')

        load_historical_payload(
            file_path=file_path,
            aios_credentials=self.aios_credentials,
            data_set_id=TestAIOpenScaleClient.data_set_id,
            days=DAYS
        )

    def test_17_get_business_payload_data(self):
        time.sleep(5)
        response = requests.get(url=self.hrefs_v2.get_data_set_records_href(TestAIOpenScaleClient.data_set_id), headers=self.ai_client._get_headers())
        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('car_new' in str(response.json()))

    def test_18_store_drift_measurements(self):
        file_path = os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'historical_records',
                                 'history_drift.json')

        load_historical_drift_measurement(
            file_path=file_path,
            aios_credentials=self.aios_credentials,
            monitor_instance_id=self.drift_instance_id,
            business_application_id=self.b_app_uid,
            days=DAYS
            )

    def test_18b_get_drift_measurements(self):
        query = '?start=2018-01-23T12:46:55.677590Z&end=2019-12-04T12:46:55.677590Z'
        metrics_url = self.hrefs_v2.get_measurements_href(self.drift_instance_id) + query
        response = requests.get(url=metrics_url, headers=self.ai_client._get_headers())

        self.assertEqual(200, response.status_code)
        print(response.json()['measurements'][0])

    def test_19_run_correlation_monitor(self):
        paylaod = {
            "ai_monitor_instance_ids": [TestAIOpenScaleClient.drift_instance_id],
            "business_app_uid": TestAIOpenScaleClient.b_app_uid
        }

        response = requests.put(
            url=self.hrefs_v2.get_monitor_instance_run_href('correlations', TestAIOpenScaleClient.corr_monitor_instance_id, '999'),
            headers=TestAIOpenScaleClient.ai_client._get_headers(),
            json=paylaod)

        print(response.json())
        self.assertEqual(response.status_code, 200)
        TestAIOpenScaleClient.subscription.monitoring.show_table('correlations')

    def test_22_check_correlations_metrics(self):
        time.sleep(20)
        query = '?start=2018-01-23T12:46:55.677590Z&end=2019-12-04T12:46:55.677590Z'
        url = self.hrefs_v2.get_measurements_href(TestAIOpenScaleClient.corr_monitor_instance_id) + query
        print(url)

        response = requests.get(url=url, headers=self.ai_client._get_headers())

        print(response.json())
        self.assertEqual(response.status_code, 200)
        self.assertTrue('significant_coefficients' in str(response.json()))

    #
    # def test_20_check_correlation_metrics(self):
    #     self.subscription.monitoring.show_table(monitor_uid=TestAIOpenScaleClient.correlation_monitor_uid)
    #     self.subscription.monitoring.print_table_schema()
    #     self.subscription.monitoring.describe_table(monitor_uid=TestAIOpenScaleClient.correlation_monitor_uid)
    #
    #     metrics = self.subscription.monitoring.get_metrics(deployment_uid=self.deployment_uid,
    #                                                        monitor_uid=TestAIOpenScaleClient.correlation_monitor_uid, format='samples')
    #     print("Metrics:\n{}".format(metrics))
    #
    #     metrics = self.subscription.monitoring.get_metrics(deployment_uid=self.deployment_uid,
    #                                                        monitor_uid=TestAIOpenScaleClient.correlation_monitor_uid, format='time_series')
    #     print("Metrics timeseries:\n{}".format(metrics))
    #
    #     python_df = TestAIOpenScaleClient.subscription.monitoring.get_table_content(
    #         monitor_uid=TestAIOpenScaleClient.correlation_monitor_uid, format="python")
    #     print(python_df)

    # def test_29_disable_monitoring(self):
    #     TestAIOpenScaleClient.subscription.monitoring.disable(TestAIOpenScaleClient.correlation_monitor_uid)
    #
    # def test_34_unsubscribe(self):
    #     self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)
    #
    # def test_35_unbind(self):
    #     self.ai_client.data_mart.bindings.delete(self.binding_uid)
    #
    # @classmethod
    # def tearDownClass(cls):
    #     print("Deleting DataMart.")
    #     cls.ai_client.data_mart.delete()
    #

if __name__ == '__main__':
    unittest.main()
