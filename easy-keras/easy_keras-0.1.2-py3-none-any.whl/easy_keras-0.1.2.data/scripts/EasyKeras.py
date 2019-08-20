from keras.utils import plot_model
import matplotlib.pyplot as plt
from keras.models import Sequential, Model
from keras.layers import Dense
from keras.optimizers import Adam

"""
Abstract Class that handles basic verbose settings that utilizes keras.
"""


class EasyModel:
    history = None
    model = None
    x, y, = None, None
    model_name = None

    def build(self, optimizer, model_name="model", model_type='sequential'):
        """
        This should be overridden for each instance of a keras model
        :param model_name: name the keras model
        :return:
        """
        raise AssertionError("Attempting to call abstract method")

    def train(self, x, y, *args, **kwargs):
        assert self.model, "Model is None, have you tried building it?"
        self.history = self.model.fit(x, y, *args, **kwargs)

    def plot_results(self, vars=None):
        assert self.model, "Attempting to call abstract method"
        if not isinstance(vars, list):
            raise ValueError("argument must in form of a list")

        for var in vars:
            plt.plot(self.history.history[var], label=var)
        plt.show()

    def summary(self, name, display_image=True):
        assert self.model, "Attempting to call abstract method"
        self.model.summary()
        image = None
        name += ".png"
        if display_image:
            from IPython.display import Image
            plot_model(self.model, to_file=name, show_shapes=True, show_layer_names=True)
            image = Image(name)

        return image

    def predict(self, x, *args, **kwargs):
        assert self.model, "Attempting to call abstract method"
        return self.model.predict(x, *args, **kwargs)


class Perceptron(EasyModel):
    def build(self, optimizer, model_name="simple_perceptron", *compile_args, **compile_kwargs):
        self.model = Sequential(name=model_name)
        self.model.add(Dense(100, input_dim=1))
        self.model.add(Dense(1))
        self.model.compile(optimizer, *compile_args, **compile_kwargs)
        return self.summary(name=model_name)


if __name__ == '__main__':
    import numpy as np
    x = (np.random.rand(1000)).reshape(-1, 1)
    y = x * x

    dense = Perceptron()
    image = dense.build(optimizer=Adam(lr=0.01), loss='mse')
    dense.train(x, y, epochs=100, verbose=2)

    x_input = np.array([0.1, 0.2, 0.3]).reshape(-1, 1)
    print(x.shape, x_input.shape)
    pred_y = dense.predict(x_input)
    print(pred_y)