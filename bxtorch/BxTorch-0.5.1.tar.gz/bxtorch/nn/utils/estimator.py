#
#  estimator.py
#  bxtorch
#
#  Created by Oliver Borchert on 09/04/19.
#  Copyright (c) 2019 Oliver Borchert. All rights reserved.
#

from bxtorch.utils.stdlib import cached_property

class Estimator:
    """
    Estimators are meant to be mixins for PyTorch modules. They extend the
    module with three additional methods:

    * `fit(...)`: This function optimizes the parameters of the model given
        some (input and output) data.
    * `evaluate(...)`: This function estimates the performance of the model by
        returning some suitable metric based on some (input and output) data. 
        This metric is usually used in the `fit` method as well (e.g. an 
        appropriate loss).
    * `predict(...)`: This function performs inference based on some (input)
        data. This method is usually tightly coupled with the model's forward
        method, however, opens additional possibilities such as easy GPU 
        support.

    Usually, the module does not implement these method itself, *unless 
    training is tightly coupled with the model parameters*. An example might be 
    a linear regression module. Normally, however, the module is expected to
    provide an `__engine__` class that accepts the module as first parameter
    (or alternatively overwrite the `engine` cached property). This engine 
    class acts as a default engine which is used whenever one of the methods is 
    called. The arguments for the functions therefore depend on the particular 
    engine that is being used.
    """

    # MARK: Initialization
    def __init__(self, *args, **kwargs):
        super(Estimator, self).__init__(*args, **kwargs)

    # MARK: Computed Properties
    @cached_property
    def engine(self):
        return type(self).__engine__(self)
        
    # MARK: Instance Methods
    def fit(self, *args, **kwargs):
        """
        Optimizes the parameters of the model based on input and output data.
        The parameters are passed to the `train` method of the model's engine.
        """
        return self.engine.train(*args, **kwargs)

    def evaluate(self, *args, **kwargs):
        """
        Estimates the performance of the model by returning some metric based
        on input and output data. The parameters are passed to the `evaluate`
        method of the model's engine.
        """
        return self.engine.evaluate(*args, **kwargs)

    def predict(self, *args, **kwargs):
        """
        Performs inference based on some input data. The parameters are passed
        to the `predict` method of the model's engine.
        """
        return self.engine.predict(*args, **kwargs)
