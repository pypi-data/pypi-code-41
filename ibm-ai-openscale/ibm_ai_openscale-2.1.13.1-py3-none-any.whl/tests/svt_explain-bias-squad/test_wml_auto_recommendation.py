# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from pyspark import SparkContext, SQLContext
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.feature import StringIndexer, VectorAssembler, IndexToString
from pyspark.sql.types import StructType, DoubleType, StringType, ArrayType

from assertions import *
from ibm_ai_openscale import APIClient, APIClient4ICP
from ibm_ai_openscale.engines import *
from ibm_ai_openscale.supporting_classes import Feature
from ibm_ai_openscale.supporting_classes.data_distribution_agg import Agg
from ibm_ai_openscale.supporting_classes.enums import InputDataType, ProblemType
from preparation_and_cleaning import *


class TestAIOpenScaleClient(unittest.TestCase):
    transaction_id = None
    ai_client = None
    deployment_uid = None
    model_uid = None
    subscription_uid = None
    wml_client = None
    subscription = None
    binding_uid = None
    aios_model_uid = None
    test_uid = str(uuid.uuid4())

    @classmethod
    def setUpClass(cls):
        cls.schema = get_schema_name()
        cls.aios_credentials = get_aios_credentials()
        cls.database_credentials = get_database_credentials()

        if "ICP" in get_env():
            cls.ai_client = APIClient4ICP(cls.aios_credentials)
            upload_credit_risk_training_data_to_db2(cls.database_credentials)

        else:
            cls.ai_client = APIClient(cls.aios_credentials)
            cls.wml_credentials = get_wml_credentials()

        prepare_env(cls.ai_client)

    def test_01_setup_data_mart(self):
        TestAIOpenScaleClient.ai_client.data_mart.setup(db_credentials=self.database_credentials, schema=self.schema)

    def test_03_bind_wml_instance(self):
        if "ICP" in get_env():
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on ICP", WatsonMachineLearningInstance4ICP())
        else:
            TestAIOpenScaleClient.binding_uid = self.ai_client.data_mart.bindings.add("WML instance on Cloud", WatsonMachineLearningInstance(self.wml_credentials))

    def test_05_get_wml_client(self):
        binding_uid = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_uids()[0]
        TestAIOpenScaleClient.wml_client = TestAIOpenScaleClient.ai_client.data_mart.bindings.get_native_engine_client(binding_uid)

    def test_06_prepare_model(self):
        asset_name = "AIOS Spark German Risk model"
        deployment_name = "AIOS Spark German Risk deployment"

        TestAIOpenScaleClient.model_uid, TestAIOpenScaleClient.deployment_uid = get_wml_model_and_deployment_id(
            model_name=asset_name, deployment_name=deployment_name)

        if self.deployment_uid is None:
            ctx = SparkContext.getOrCreate()
            sc = SQLContext(ctx)

            spark_df = sc.read.format("com.databricks.spark.csv").option("header", "true").option("delimiter", ",").option("inferSchema", "true").load(
                os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'credit_risk_training.csv'))
            spark_df.printSchema()

            (train_data, test_data) = spark_df.randomSplit([0.8, 0.2], 24)
            print("Number of records for training: " + str(train_data.count()))
            print("Number of records for evaluation: " + str(test_data.count()))

            si_CheckingStatus = StringIndexer(inputCol='CheckingStatus', outputCol='CheckingStatus_IX')
            si_CreditHistory = StringIndexer(inputCol='CreditHistory', outputCol='CreditHistory_IX')
            si_LoanPurpose = StringIndexer(inputCol='LoanPurpose', outputCol='LoanPurpose_IX')
            si_ExistingSavings = StringIndexer(inputCol='ExistingSavings', outputCol='ExistingSavings_IX')
            si_EmploymentDuration = StringIndexer(inputCol='EmploymentDuration', outputCol='EmploymentDuration_IX')
            si_Sex = StringIndexer(inputCol='Sex', outputCol='Sex_IX')
            si_OthersOnLoan = StringIndexer(inputCol='OthersOnLoan', outputCol='OthersOnLoan_IX')
            si_OwnsProperty = StringIndexer(inputCol='OwnsProperty', outputCol='OwnsProperty_IX')
            si_InstallmentPlans = StringIndexer(inputCol='InstallmentPlans', outputCol='InstallmentPlans_IX')
            si_Housing = StringIndexer(inputCol='Housing', outputCol='Housing_IX')
            si_Job = StringIndexer(inputCol='Job', outputCol='Job_IX')
            si_Telephone = StringIndexer(inputCol='Telephone', outputCol='Telephone_IX')
            si_ForeignWorker = StringIndexer(inputCol='ForeignWorker', outputCol='ForeignWorker_IX')
            si_Label = StringIndexer(inputCol="Risk", outputCol="label").fit(spark_df)
            label_converter = IndexToString(inputCol="prediction", outputCol="predictedLabel", labels=si_Label.labels)

            va_features = VectorAssembler(
                inputCols=["CheckingStatus_IX", "CreditHistory_IX", "LoanPurpose_IX", "ExistingSavings_IX",
                           "EmploymentDuration_IX", "Sex_IX", "OthersOnLoan_IX", "OwnsProperty_IX", "InstallmentPlans_IX",
                           "Housing_IX", "Job_IX", "Telephone_IX", "ForeignWorker_IX", "LoanDuration", "LoanAmount",
                           "InstallmentPercent", "CurrentResidenceDuration", "LoanDuration", "Age", "ExistingCreditsCount",
                           "Dependents"], outputCol="features")

            classifier = RandomForestClassifier(featuresCol="features")

            pipeline = Pipeline(
                stages=[si_CheckingStatus, si_CreditHistory, si_EmploymentDuration, si_ExistingSavings, si_ForeignWorker,
                        si_Housing, si_InstallmentPlans, si_Job, si_LoanPurpose, si_OthersOnLoan,
                        si_OwnsProperty, si_Sex, si_Telephone, si_Label, va_features, classifier, label_converter])

            model = pipeline.fit(train_data)
            predictions = model.transform(test_data)
            evaluator = BinaryClassificationEvaluator(rawPredictionCol="prediction")
            auc = evaluator.evaluate(predictions)

            print("Accuracy = %g" % auc)

            train_data_schema = spark_df.schema
            label_field = next(f for f in train_data_schema.fields if f.name == "Risk")
            label_field.metadata['values'] = si_Label.labels
            input_fileds = filter(lambda f: f.name != "Risk", train_data_schema.fields)

            output_data_schema = StructType(list(input_fileds)). \
                add("prediction", DoubleType(), True, {'modeling_role': 'prediction'}). \
                add("predictedLabel", StringType(), True,
                    {'modeling_role': 'decoded-target', 'values': si_Label.labels}). \
                add("probability", ArrayType(DoubleType()), True, {'modeling_role': 'probability'})

            if "ICP" in get_env():
                training_data_reference = {
                    "name": "Credit Risk feedback",
                    "connection": self.database_credentials,
                    "source": {
                        "tablename": "CREDIT_RISK_TRAINING",
                        'schema_name': 'TRAININGDATA',
                        "type": "db2"
                    }
                }
            else:
                db2_credentials = {
                    "hostname": "dashdb-entry-yp-dal09-10.services.dal.bluemix.net",
                    "password": "89TsmoAN_Sb_",
                    "https_url": "https://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:8443",
                    "port": 50000,
                    "ssldsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-dal09-10.services.dal.bluemix.net;PORT=50001;PROTOCOL=TCPIP;UID=dash14647;PWD=89TsmoAN_Sb_;Security=SSL;",
                    "host": "dashdb-entry-yp-dal09-10.services.dal.bluemix.net",
                    "jdbcurl": "jdbc:db2://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
                    "uri": "db2://dash14647:89TsmoAN_Sb_@dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50000/BLUDB",
                    "db": "BLUDB",
                    "dsn": "DATABASE=BLUDB;HOSTNAME=dashdb-entry-yp-dal09-10.services.dal.bluemix.net;PORT=50000;PROTOCOL=TCPIP;UID=dash14647;PWD=89TsmoAN_Sb_;",
                    "username": "dash14647",
                    "ssljdbcurl": "jdbc:db2://dashdb-entry-yp-dal09-10.services.dal.bluemix.net:50001/BLUDB:sslConnection=true;"
                }

                training_data_reference = {
                    "name": "Credit Risk feedback",
                    "connection": db2_credentials,
                    "source": {
                        "tablename": "CREDIT_RISK_TRAINING",
                        "type": "dashdb"
                    }
                }

            #print("Training data reference:\n{}".format(training_data_reference))

            model_props = {
                self.wml_client.repository.ModelMetaNames.NAME: "{}".format(asset_name),
                self.wml_client.repository.ModelMetaNames.TRAINING_DATA_REFERENCE: training_data_reference,
                self.wml_client.repository.ModelMetaNames.OUTPUT_DATA_SCHEMA: output_data_schema.jsonValue(),
                self.wml_client.repository.ModelMetaNames.EVALUATION_METRICS: [
                    {
                        "name": "AUC",
                        "value": auc,
                        "threshold": 0.8
                    }
                ]
            }

            print("Publishing a new model...")
            published_model_details = self.wml_client.repository.store_model(model=model, meta_props=model_props, training_data=train_data, pipeline=pipeline)

            #print("Published model details:\n{}".format(published_model_details))
            TestAIOpenScaleClient.model_uid = self.wml_client.repository.get_model_uid(published_model_details)

            print("Deploying model: {}, deployment name: {}".format(asset_name, deployment_name))
            deployment = self.wml_client.deployments.create(artifact_uid=self.model_uid, name=deployment_name, asynchronous=False)
            TestAIOpenScaleClient.deployment_uid = self.wml_client.deployments.get_uid(deployment)

            deployment_details = self.wml_client.deployments.get_details(self.deployment_uid)
            #print("Deployment details:\n{}".format(deployment_details))

    def test_07_subscribe(self):
        # get_details_from_restapi(ai_client=self.ai_client, binding_uid=self.binding_uid)

        subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.add(WatsonMachineLearningAsset(
            source_uid=TestAIOpenScaleClient.model_uid,
            binding_uid=self.binding_uid,
            problem_type=ProblemType.BINARY_CLASSIFICATION,
            input_data_type=InputDataType.STRUCTURED,
            prediction_column='predictedLabel',
            probability_column='probability',
            feature_columns=['CheckingStatus', 'LoanDuration', 'CreditHistory', 'LoanPurpose', 'LoanAmount',
                             'ExistingSavings', 'EmploymentDuration', 'InstallmentPercent', 'Sex', 'OthersOnLoan',
                             'CurrentResidenceDuration', 'OwnsProperty', 'Age', 'InstallmentPlans', 'Housing',
                             'ExistingCreditsCount', 'Job', 'Dependents', 'Telephone', 'ForeignWorker'],
            categorical_columns=['CheckingStatus', 'CreditHistory', 'LoanPurpose', 'ExistingSavings',
                                 'EmploymentDuration', 'Sex', 'OthersOnLoan', 'OwnsProperty', 'InstallmentPlans',
                                 'Housing', 'Job', 'Telephone', 'ForeignWorker']
        ))

        # WORKAROUND FOR #8237 issue
        if "ICP" in get_env():
            db_cr = self.database_credentials
            db_cr['database_name'] = self.database_credentials['db']
            db_cr['connection_string'] = self.database_credentials['jdbcurl']

            tdr = {
                'type': 'db2',
                "name": "Credit Risk feedback",
                "connection": db_cr,
                "location": {
                    "tablename": "CREDIT_RISK_TRAINING",
                    "schema_name": "TRAININGDATA",
                }
            }

            subscription.update(training_data_reference=tdr)

        TestAIOpenScaleClient.subscription_uid = subscription.uid

        TestAIOpenScaleClient.subscription = TestAIOpenScaleClient.ai_client.data_mart.subscriptions.get(TestAIOpenScaleClient.subscription_uid)

    
    def test_08_getup_fairness_recommendations(self):
        favourable_classes=['No Risk']
        unfavourable_classes=['Risk']
        recommendations = TestAIOpenScaleClient.subscription.fairness_monitoring.recommend_attributes(favourable_classes=favourable_classes, unfavourable_classes=unfavourable_classes)
        expected_attributes = ["Age", "Sex"]
        assert_fairness_recommended_attributes(recommendations, expected_attributes)
        print(recommendations)
        
    @classmethod
    def tearDownClass(cls):
        cls.ai_client.data_mart.subscriptions.delete(cls.subscription.uid)
        
        cls.ai_client.data_mart.bindings.delete(cls.binding_uid, background_mode=True)
        time.sleep(5)
        
        print("Deleting DataMart.")
        cls.ai_client.data_mart.delete()

        # clean_wml_instance(model_id=cls.model_uid, deployment_id=cls.deployment_uid)


if __name__ == '__main__':
    unittest.main()
