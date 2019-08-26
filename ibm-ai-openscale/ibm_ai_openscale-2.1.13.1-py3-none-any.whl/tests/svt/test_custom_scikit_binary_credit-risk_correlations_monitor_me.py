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
from ibm_ai_openscale.utils.inject_historical_data import load_historical_measurement, load_historical_payload, load_historical_drift_measurement

from ibm_ai_openscale.supporting_classes import Feature
from ibm_ai_openscale.supporting_classes.measurement_record import MeasurementRecord


DAYS = 1


class TestAIOpenScaleClient(unittest.TestCase):
    subscription_s1 = None
    subscription_s2 = None
    subscription_s3 = None

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

    def test_05a_subscribe_custom(self):
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
        TestAIOpenScaleClient.subscription_s1 = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)

    def test_05b_subscribe_custom(self):
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
        TestAIOpenScaleClient.subscription_s2 = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)

    def test_05c_subscribe_custom(self):
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
        TestAIOpenScaleClient.subscription_s3 = self.ai_client.data_mart.subscriptions.get(self.subscription_uid)

    def test_06_score_model_and_log_payload(self):
        request, response, response_time = self.score(self.subscription_s1.get_details())
        print('response: ' + str(response))

        records_list = []

        for i in range(0, 5):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription_s1.payload_logging.store(records=records_list)

        for i in range(0, 5):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription_s2.payload_logging.store(records=records_list)

        for i in range(0, 5):
            records_list.append(PayloadRecord(request=request, response=response, response_time=response_time))

        self.subscription_s3.payload_logging.store(records=records_list)

    def test_08_stats_on_payload_logging_table(self):
        time.sleep(10)

    def test_09_enable_drift(self):
        self.subscription_s1.drift_monitoring.enable(threshold=0.6, min_records=10, model_path=os.path.join(self.drift_model_path, self.drift_model_name))
        drift_monitor_details = self.subscription_s1.monitoring.get_details(monitor_uid='drift')
        print('drift monitor details', drift_monitor_details)

    def test_10_run_drift(self):
        result = self.subscription_s1.drift_monitoring.run(background_mode=False)
        print('drift run', result)
        self.assertTrue('predicted_accuracy' in str(result))

    def test_11_setup_quality_monitoring(self):
        self.subscription_s1.quality_monitoring.enable(threshold=0.8, min_records=5)

    def test_12_setup_fairness_monitoring(self):
        from ibm_ai_openscale.supporting_classes import Feature

        self.assertIsNotNone(TestAIOpenScaleClient.data_df)

        TestAIOpenScaleClient.subscription_s2.fairness_monitoring.enable(
            features=[
                Feature("Sex", majority=['male'], minority=['female'], threshold=0.95),
                Feature("Age", majority=[[26, 75]], minority=[[18, 25]], threshold=0.95)
            ],
            favourable_classes=['No Risk'],
            unfavourable_classes=['Risk'],
            min_records=4,
            training_data=TestAIOpenScaleClient.data_df)

    def test_13_inject_quality_metrics(self):
        quality_metric = {'area_under_roc': 0.666}
        self.subscription_s1.monitoring.store_metrics(monitor_uid='quality', metrics=quality_metric)

        time.sleep(10)

        self.subscription_s1.quality_monitoring.show_table()
        self.subscription_s1.monitoring.show_table(monitor_uid='quality')

        quality_metrics_py = self.subscription_s1.quality_monitoring.get_table_content(format='python')
        self.assertTrue('0.666' in str(quality_metrics_py))

    def test_14_inject_quality_measurements(self):
        quality_metric = {'area_under_roc': 0.999}
        source = {
            "id": "confusion_matrix_1",
            "type": "confusion_matrix",
            "data": {
                "labels": ["Risk", "No Risk"],
                "values": [[11, 21],
                           [20, 10]]}
        }

        measurements = [
            MeasurementRecord(metrics=quality_metric, sources=source),
            MeasurementRecord(metrics=quality_metric, sources=source)
        ]

        details = self.subscription_s1.monitoring.store_measurements(monitor_uid='quality', measurements=measurements)
        print('Measurement details', details)

        time.sleep(10)

        measurement_id = details[0]['measurement_id']

        print('measurement_id', measurement_id)
        self.subscription_s1.quality_monitoring.show_table()
        self.subscription_s1.quality_monitoring.show_confusion_matrix(measurement_id=measurement_id)

        quality_metrics_py = self.subscription_s1.quality_monitoring.get_table_content(format='python')
        self.assertTrue(str(quality_metric['area_under_roc']) in str(quality_metrics_py))
        self.assertTrue('20' in str(quality_metrics_py))

        self.subscription_s1.quality_monitoring.show_table()
        self.subscription_s1.monitoring.show_table(monitor_uid='quality')

    def test_15_inject_performance_metrics(self):
        if "ICP" in get_env():
            self.skipTest("Performance monitoring is not working on ICP with WML scoring.")

        performance_metric = {'records': 245, 'response_time': 62.33809845686894}
        self.subscription_s1.monitoring.store_metrics(monitor_uid='performance', metrics=performance_metric)

        time.sleep(10)

        self.subscription_s1.performance_monitoring.show_table()

        performance_table_python = self.subscription_s1.performance_monitoring.get_table_content(format='python')
        self.assertTrue('62.33809845686894' in str(performance_table_python))

    def test_16_inject_performance_measurements(self):
        measurements = [
            MeasurementRecord(metrics={'records': 245, 'response_time': 62.33809845686894}),
            MeasurementRecord(metrics={'records': 45, 'response_time': 2.33809845686894})
        ]

        details = self.subscription_s1.monitoring.store_measurements(monitor_uid='performance',
                                                                               measurements=measurements)
        time.sleep(10)

        self.assertTrue('2.33809845686894' in str(details))

    def test_17_inject_fairness_metrics(self):
        fairness_metric = {'metrics': [{'feature': 'Sex', 'majority': {'values': [{'value': 'male', 'distribution': {'male': [{'count': 65, 'label': 'No Risk', 'is_favourable': True}, {'count': 4, 'label': 'Risk', 'is_favourable': False}]}, 'fav_class_percent': 95.0}], 'total_fav_percent': 95.0, 'total_rows_percent': 33.33333333333333}, 'minority': {'values': [{'value': 'female', 'is_biased': True, 'distribution': {'female': [{'count': 29, 'label': 'No Risk', 'is_favourable': True}, {'count': 2, 'label': 'Risk', 'is_favourable': False}]}, 'fairness_value': 0.947333, 'fav_class_percent': 90.0}], 'total_fav_percent': 90.0, 'total_rows_percent': 33.33333333333333}}, {'feature': 'Age', 'majority': {'values': [{'value': [26, 75], 'distribution': {'26': [{'count': 4, 'label': 'No Risk', 'is_favourable': True}], '28': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '29': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '30': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '31': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '32': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '33': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '34': [{'count': 1, 'label': 'Risk', 'is_favourable': False}, {'count': 4, 'label': 'No Risk', 'is_favourable': True}], '35': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '36': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}], '37': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '38': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '39': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}, {'count': 1, 'label': 'Risk', 'is_favourable': False}], '40': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}], '41': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}], '43': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '45': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '47': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '49': [{'count': 1, 'label': 'Risk', 'is_favourable': False}], '50': [{'count': 3, 'label': 'No Risk', 'is_favourable': True}, {'count': 1, 'label': 'Risk', 'is_favourable': False}], '52': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '54': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '55': [{'count': 1, 'label': 'Risk', 'is_favourable': False}, {'count': 1, 'label': 'No Risk', 'is_favourable': True}], '71': [{'count': 1, 'label': 'Risk', 'is_favourable': False}]}, 'fav_class_percent': 88.43537414965986}], 'total_fav_percent': 88.43537414965986, 'total_rows_percent': 49.0}, 'minority': {'values': [{'value': [18, 25], 'is_biased': False, 'distribution': {'19': [{'count': 16, 'label': 'No Risk', 'is_favourable': True}], '20': [{'count': 16, 'label': 'No Risk', 'is_favourable': True}], '21': [{'count': 11, 'label': 'No Risk', 'is_favourable': True}], '23': [{'count': 2, 'label': 'No Risk', 'is_favourable': True}], '24': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}], '25': [{'count': 1, 'label': 'No Risk', 'is_favourable': True}]}, 'fairness_value': 1.101, 'fav_class_percent': 97.38562091503267}], 'total_fav_percent': 97.38562091503267, 'total_rows_percent': 51.0}, 'bias_source': {'values': []}}], 'score_type': 'desperate impact', 'response_time': '13.128683', 'rows_analyzed': 100, 'perturbed_data_size': 200, 'manual_labelling_store': 'Manual_Labeling_dd79dd1b-0afc-436e-9999-6fd6414f81c2'}
        self.subscription_s2.monitoring.store_metrics(monitor_uid='fairness', metrics=fairness_metric)

        time.sleep(10)

        self.subscription_s2.fairness_monitoring.show_table()

        python_table_content = self.subscription_s2.fairness_monitoring.get_table_content(format='python')
        self.assertTrue('0.947333' in str(python_table_content))

    def test_18_enable_drift(self):
        self.subscription_s3.drift_monitoring.enable(threshold=0.6, min_records=10,
                                                     model_path=os.path.join(self.drift_model_path,
                                                                             self.drift_model_name))
        drift_monitor_details = self.subscription_s3.monitoring.get_details(monitor_uid='drift')
        print('drift monitor details', drift_monitor_details)

    def test_19_run_drift(self):
        result = self.subscription_s3.drift_monitoring.run(background_mode=False)
        print('drift run', result)
        self.assertTrue('predicted_accuracy' in str(result))

    def test_20_get_details(self):

        print("all subscriptions:")
        print(self.ai_client.data_mart.subscriptions.get_details())

        print("\nsubscription 1:")
        print(self.subscription_s1.get_details())

        print("subscription 1 metrics:")
        print(self.subscription_s1.get_deployment_metrics())

        print("\nsubscription 2:")
        print(self.subscription_s2.get_details())

        print("subscription 2 metrics:")
        print(self.subscription_s2.get_deployment_metrics())

        print("\nsubscription 3:")
        print(self.subscription_s3.get_details())

        print("subscription 3 metrics:")
        print(self.subscription_s3.get_deployment_metrics())

        print("All metrics:\n")
        print(self.ai_client.data_mart.get_deployment_metrics())


if __name__ == '__main__':
    unittest.main()
