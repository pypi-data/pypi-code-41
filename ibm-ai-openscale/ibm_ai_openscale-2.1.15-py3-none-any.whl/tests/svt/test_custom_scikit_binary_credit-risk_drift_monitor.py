# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import pandas as pd
import requests

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from sklearn.externals import joblib
from ibm_ai_openscale.supporting_classes.payload_record import PayloadRecord


class TestAIOpenScaleClient(unittest.TestCase):

    ai_client = None
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    scoring_url = None
    labels = None
    wml_client = None
    subscription = None
    binding_uid = None
    aios_model_uid = None
    scoring_result = None
    payload_scoring = None
    published_model_details = None
    source_uid = None
    transaction_id = None
    feedback_records = None
    start_date = datetime.utcnow().isoformat() + 'Z'
    drift_model_name = "drift_detection_model.tar.gz"
    drift_model_path = os.path.join(os.getcwd(), 'artifacts', 'drift_models')
    feature_columns = ['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                       'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex', 'OthersOnLoan',
                       'CurrentResidenceDuration', 'OwnsProperty', 'Age', 'InstallmentPlans', 'Housing',
                       'ExistingCreditsCount', 'Job', 'Dependents', 'Telephone', 'ForeignWorker']
    categorical_columns = ['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                           'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty', 'InstallmentPlans',
                           'Housing', 'Job', 'Telephone', 'ForeignWorker']
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

    def score_4_drift(self, training_data):
        import numpy as np

        # credit_model_path = os.path.join(os.getcwd(), 'artifacts', 'credit-risk', 'german_credit_risk.joblib')
        # credit_model = joblib.load(credit_model_path)
        # probabilities = credit_model['model'].predict_proba(training_data).tolist()
        # predictions = credit_model['postprocessing'](credit_model['model'].predict(training_data))

        import pickle

        probs1k_filepath = os.path.join(self.drift_model_path, 'probs1k')
        preds1k_filepath = os.path.join(self.drift_model_path, 'preds1k')
        probs4k_filepath = os.path.join(self.drift_model_path, 'probs4k')
        preds4k_filepath = os.path.join(self.drift_model_path, 'preds4k')

        if training_data.shape[0] == 4000:
            # with open(probs4k_filepath, 'wb') as fp:
            #     pickle.dump(probabilities, fp)
            #
            # with open(preds4k_filepath, 'wb') as fp:
            #     pickle.dump(predictions, fp)

            with open(probs4k_filepath, 'rb') as fp:
                probabilities = pickle.load(fp)

            with open(preds4k_filepath, 'rb') as fp:
                predictions = pickle.load(fp)

        elif training_data.shape[0] == 1000:
            # with open(probs1k_filepath, 'wb') as fp:
            #     pickle.dump(probabilities, fp)
            #
            # with open(preds1k_filepath, 'wb') as fp:
            #     pickle.dump(predictions, fp)

            with open(probs1k_filepath, 'rb') as fp:
                probabilities = pickle.load(fp)

            with open(preds1k_filepath, 'rb') as fp:
                predictions = pickle.load(fp)

        print('probs size', len(probabilities))
        print('preds size', len(predictions))
        print('training data size', self.data_df.shape[0])

        return np.array(probabilities), predictions

    def generate_drift_model(self):
        from ibm_ai_openscale.utils.drift_trainer import DriftTrainer
        drift_detection_input = {
            "feature_columns": self.feature_columns,
            "categorical_columns": self.categorical_columns,
            "label_column": 'Risk',
            "problem_type": "binary"
        }

        drift_trainer = DriftTrainer(self.data_df, drift_detection_input)
        drift_trainer.generate_drift_detection_model(
            self.score_4_drift, batch_size=self.data_df.shape[0])
        drift_trainer.learn_constraints()
        print('filepath', self.drift_model_path, self.drift_model_name)

        DriftTrainer.create_model_tar(
            drift_detection_model=drift_trainer.drift_detection_model, constraints=drift_trainer.constraints, path_prefix=self.drift_model_path+'/', file_name=self.drift_model_name)

    def score(self, subscription_details):
        fields = ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount", "ExistingSavings",
                  "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan", "CurrentResidenceDuration",
                  "OwnsProperty", "Age", "InstallmentPlans", "Housing", "ExistingCreditsCount", "Job", "Dependents",
                  "Telephone", "ForeignWorker"]
        values = [
            ["no_checking", 13, "credits_paid_to_date", "car_new", 1343, "100_to_500", "1_to_4", 2, "female", "none", 3,
             "savings_insurance", 25, "none", "own", 2, "skilled", 1, "none", "yes"],
            ["no_checking", 24, "prior_payments_delayed", "furniture", 4567, "500_to_1000", "1_to_4", 4, "male", "none",
             4, "savings_insurance", 60, "none", "free", 2, "management_self-employed", 1, "none", "yes"],
            ["0_to_200", 26, "all_credits_paid_back", "car_new", 863, "less_100", "less_1", 2, "female", "co-applicant",
             2, "real_estate", 38, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 14, "no_credits", "car_new", 2368, "less_100", "1_to_4", 3, "female", "none", 3, "real_estate",
             29, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["0_to_200", 4, "no_credits", "car_new", 250, "less_100", "unemployed", 2, "female", "none", 3,
             "real_estate", 23, "none", "rent", 1, "management_self-employed", 1, "none", "yes"],
            ["no_checking", 17, "credits_paid_to_date", "car_new", 832, "100_to_500", "1_to_4", 2, "male", "none", 2,
             "real_estate", 42, "none", "own", 1, "skilled", 1, "none", "yes"],
            ["no_checking", 50, "outstanding_credit", "appliances", 5696, "unknown", "greater_7", 4, "female",
             "co-applicant", 4, "unknown", 54, "none", "free", 2, "skilled", 1, "yes", "yes"],
            ["0_to_200", 13, "prior_payments_delayed", "retraining", 1375, "100_to_500", "4_to_7", 3, "male", "none", 3,
             "real_estate", 70, "none", "own", 2, "management_self-employed", 1, "none", "yes"]
        ]

        payload = {"fields": fields, "values": values}
        header = {'Content-Type': 'application/json',
                  'Authorization': 'Bearer xxx'}
        scoring_url = subscription_details['entity']['deployments'][0]['scoring_endpoint']['url']

        response = requests.post(scoring_url, json=payload, headers=header)

        return payload, response.json(), 25

    @classmethod
    def setUpClass(cls):
        try:
            requests.get(
                url="{}/v1/deployments".format(cls.credentials['url']), timeout=10)
        except:
            raise unittest.SkipTest("Custom app is not available.")

        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
        else:
            cls.ai_client = APIClient(cls.aios_credentials)

        prepare_env(cls.ai_client)

    def test_00_drift_model(self):
        self.skipTest("new wrapper for model training is needed @Paratap")
        self.generate_drift_model()

    def test_01_setup_data_mart(self):
        self.ai_client.data_mart.setup(
            db_credentials=self.database_credentials, schema=self.schema)

    def test_02_bind_custom(self):
        TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add(
            "My Custom deployment", CustomMachineLearningInstance(self.credentials))
        print("Binding uid: {}".format(self.binding_uid))
        self.assertIsNotNone(self.binding_uid)

    def test_03_get_binding_details(self):
        binding_details = self.ai_client.data_mart.bindings.get_details()
        print("Binding details: {}".format(binding_details))
        self.assertIsNotNone(binding_details)

    def test_04_get_deployments(self):
        print('Available deployments: {}'.format(
            self.ai_client.data_mart.bindings.list_assets()))
        self.ai_client.data_mart.bindings.list_assets()
        self.ai_client.data_mart.bindings.get_asset_details()

    def test_05_subscribe_custom(self):
        subscription = self.ai_client.data_mart.subscriptions.add(
            CustomMachineLearningAsset(
                source_uid='credit',
                label_column='Risk',
                prediction_column='prediction',
                probability_column='probability',
                feature_columns=self.feature_columns,
                categorical_columns=self.categorical_columns,
                binding_uid=self.binding_uid))

        TestAIOpenScaleClient.subscription_uid = subscription.uid
        print('Subscription details: ', subscription.get_details())
        print("Subscription id: {}".format(self.subscription_uid))
        self.assertIsNotNone(self.subscription_uid)

    def test_06_select_asset_and_get_details(self):
        TestAIOpenScaleClient.subscription = self.ai_client.data_mart.subscriptions.get(
            TestAIOpenScaleClient.subscription_uid)
        self.assertIsNotNone(self.subscription)

    def test_07_list_deployments(self):
        print("Listing deployments:\n")
        self.subscription.list_deployments()

    def test_08_validate_default_subscription_configuration(self):
        subscription_details = TestAIOpenScaleClient.subscription.get_details()

        for configuration in subscription_details['entity']['configurations']:
            if configuration['type'] == 'payload_logging' or configuration['type'] == 'performance_monitoring':
                self.assertEqual(configuration['enabled'], True)
            else:
                self.assertEqual(configuration['enabled'], False)

    def test_09_score_model_and_log_payload(self):
        request, response, response_time = self.score(
            self.subscription.get_details())

        print('response: ' + str(response))

        records_list = []

        for i in range(0, 20):
            records_list.append(PayloadRecord(
                request=request, response=response, response_time=response_time))

        self.subscription.payload_logging.store(records=records_list)

        # Add extra time for the 160 records:
        time.sleep(60)

    def test_10_stats_on_payload_logging_table(self):
        wait_for_payload_table(
            subscription=self.subscription, payload_records=160)

        self.subscription.payload_logging.print_table_schema()
        self.subscription.payload_logging.show_table()

        table_content = self.subscription.payload_logging.get_table_content()
        assert_payload_logging_pandas_table_content(pandas_table_content=table_content,
                                                    scoring_records=160)

        print('subscription details',
              TestAIOpenScaleClient.subscription.get_details())

    def test_11_enable_drift(self):
        self.subscription.drift_monitoring.enable(threshold=0.6, min_records=10, model_path=os.path.join(
            self.drift_model_path, self.drift_model_name))
        drift_monitor_details = self.subscription.monitoring.get_details(
            monitor_uid='drift')
        print('drift monitor details', drift_monitor_details)

    def test_15_run_drift(self):
        result = self.subscription.drift_monitoring.run(background_mode=False)
        print('drift run', result)
        self.assertTrue('predicted_accuracy' in str(result))

    def test_16_get_drift_metrics(self):
        time.sleep(5)
        metrics = self.subscription.drift_monitoring.get_metrics(
            deployment_uid=TestAIOpenScaleClient.deployment_uid)
        print('metrics', metrics)
        self.assertTrue('predicted_accuracy' in str(metrics))

    def test_17_stats_on_drift_monitoring_table(self):
        TestAIOpenScaleClient.subscription.drift_monitoring.print_table_schema()
        TestAIOpenScaleClient.subscription.drift_monitoring.show_table()
        TestAIOpenScaleClient.subscription.drift_monitoring.describe_table()

        pandas_df = TestAIOpenScaleClient.subscription.drift_monitoring.get_table_content()
        assert_fairness_monitoring_pandas_table_content(
            pandas_table_content=pandas_df)

        python_table_content = TestAIOpenScaleClient.subscription.drift_monitoring.get_table_content(
            format='python')
        assert_fairness_monitoring_python_table_content(
            python_table_content=python_table_content)

    def test_18_disable_monitors(self):
        self.subscription.payload_logging.disable()
        self.subscription.performance_monitoring.disable()
        self.subscription.drift_monitoring.disable()

        subscription_details = self.subscription.get_details()
        assert_monitors_enablement(subscription_details=subscription_details)

    def test_19_unsubscribe(self):
        self.ai_client.data_mart.subscriptions.delete(self.subscription.uid)

    def test_20_unbind(self):
        self.ai_client.data_mart.bindings.delete(self.binding_uid)

    @classmethod
    def tearDownClass(cls):
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()


if __name__ == '__main__':
    unittest.main()
