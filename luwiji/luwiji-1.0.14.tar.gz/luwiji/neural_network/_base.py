import os
from IPython.display import Image


class BaseIllustrationNeuralNetwork:
    def __init__(self):
        here = os.path.dirname(__file__)
        self.deep_learning = Image(f"{here}/assets/deep_learning.png", width=800)
        self.node_linear = Image(f"{here}/assets/node_linear.png", width=300)
        self.node_representation= Image(f"{here}/assets/node_representation.png", width=800)
        self.regressor = Image(f"{here}/assets/nn_regressor.png", width=500)
        self.classifier = Image(f"{here}/assets/nn_classifier.png", width=500)
        self.vocab = Image(f"{here}/assets/nn_vocab.png", width=600)
        self.layer = Image(f"{here}/assets/nn_layer.png", width=600)
        self.quiz = Image(f"{here}/assets/nn_quiz.png", width=900)
        self.activation = Image(f"{here}/assets/activation.png", width=900)
        self.think_wide = Image(f"{here}/assets/think_wide.png", width=800)
        self.think_deep = Image(f"{here}/assets/think_deep.png", width=800)
        self.less_feature = Image(f"{here}/assets/less_feature.png", width=800)
        self.spiral_genius = Image(f"{here}/assets/spiral_genius.png", width=800)
        self.momentum = Image(f"{here}/assets/momentum.png", width=800)
        self.adaptive_optimizer = Image(f"{here}/assets/optimizer.gif", width=600)
        self.dropout_idea = Image(f"{here}/assets/dropout0.png", width=800)
        self.dropout = Image(f"{here}/assets/dropout1.png", width=800)
        self.dropout_balance = Image(f"{here}/assets/dropout2.png", width=400)
        self.training_loop = Image(f"{here}/assets/training_loop.png", width=800)
        self.pytorch = Image(f"{here}/assets/pytorch.png", width=900)
        self.nomenklatur = Image(f"{here}/assets/nomenklatur.png", width=800)
