# libs
import xgboost as xgb
from sklearn.pipeline import Pipeline

# packages
from ukchurn_classification_model.config import config
from ukchurn_classification_model.preprocessors import categorical_encoder as ce
from ukchurn_classification_model.preprocessors import categorical_imputer as ci
from ukchurn_classification_model.preprocessors import numerical_imputer as ni


churn_pipeline = Pipeline(
    [
        ('categorical_imputer',
         ci.CategoricalImputer(variables=config.CATEGORICAL_VARS_WITH_NA)),
        ('numerical_imputer',
         ni.NumericalImputer(variables=config.NUMERICAL_VARS_WITH_NA)),
        ('numerical_zero_imputer',
         ni.ZeroImputer(variables=config.NUMERICAL_VARS_WITH_NA_ZERO)),
        ('categorical_encoder',
         ce.CategoricalEncoder(variables=config.CATEGORICAL_VARS)),
        ('classification_model',
         xgb.XGBClassifier(max_depth=6, learning_rate=0.1, n_estimators=100, random_state=0))
    ],
    verbose=True
)
