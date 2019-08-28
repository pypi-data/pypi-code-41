from enum import Enum, unique

@unique
class MLEngineType(Enum):
    WML = 'IBM Watson Machine Learning'
    SAGEMAKER = 'Amazon Sagemaker'
    CUSTOM = 'Custom Machine Learning Engine'
    SPSS = 'IBM SPSS C&DS'
    AZUREMLSTUDIO = 'Microsoft Azure Machine Learning Studio'
    AZUREMLSERVICE = 'Microsoft Azure Machine Learning Service'

@unique
class ResetType(Enum):
    METRICS = 'metrics'
    MONITORS = 'monitors'
    DATAMART = 'datamart'
    MODEL = 'model'
    ALL = 'all'
