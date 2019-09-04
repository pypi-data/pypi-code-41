'''
█▀▀█ █  █ █▀▀▄ █▀▀▄ █
█▄▄█ █  █ █  █ █  █ █
▀  ▀ ▀▀▀▀ ▀  ▀ ▀  ▀ ▀▀▀
Another Unnecessary Neural Network Library
Version 3.0.3 Gamma
@author "Aditya Radhakrishnan"
'''

import sys, math, random, warnings, types

import numpy as np
import pickle as pkl
from scipy.stats import logistic

class losses:

    def MSE(netop, output, df=False):
        if df:
            return np.dot(2, np.subtract(netop, output))
        return np.sum(np.square(np.subtract(netop, output)))

class activations:

    def sigmoid(x, df=False):
        y = logistic.cdf(x) # 1 / (1 + math.exp(-x))
        if df:
            return y * (1 - y)
        return y

    def stable_sigmoid(x, df=False):
        pos_mask = (x >= 0)
        neg_mask = (x < 0)
        z = np.zeros_like(x,dtype=float)
        z[pos_mask] = np.exp(-x[pos_mask])
        z[neg_mask] = np.exp(x[neg_mask])
        top = np.ones_like(x, dtype=float)
        top[neg_mask] = z[neg_mask]
        y = top / (1 + z)
        if df:
            return y * (1 - y)
        return y

    def relu(x, df=False):
        if df:
            return np.where(x > 0, 1.0, 0.0)
        return abs(x) * (x > 0)

    def leaky_relu(x, df=False, a=0.01):
        if df:
            df = np.ones_like(x)
            df[x < 0] = a
            return df
        return np.where(x > 0, x, x * a)

    def linear(x, df=False):
        if df:
            return np.ones(x.shape)
        return x

class NeuralNetwork:

    def __init__(self, struct=[], actfunc="sigmoid"):
        self.struct = struct
        if isinstance(actfunc, str) or isinstance(actfunc, types.FunctionType):
            actfunc = [actfunc] * (len(self.struct) - 1)
        else:
            if len(actfunc) is not (len(struct) - 1):
                warnings.warn("Number of activations specified (" + str(len(actfunc)) + ") does not match number of non-input layers specified (" + str(len(struct) - 1) + ").")
        self.actfunc = actfunc
        del actfunc
        for x in range(len(self.actfunc)):
            if isinstance(self.actfunc[x], str):
                try:
                    exec("activations." + self.actfunc[x])
                except:
                    warnings.warn("Activation function specified (" + self.actfunc[x] + ") is not defined.")
                else:
                    self.actfunc[x] = eval("activations." + self.actfunc[x])
        if struct != []:
            if self.actfunc[-1] is activations.relu:
                warnings.warn("ReLU fails as the activation function for the last/output layer.")
        self.weights = [None] * (len(struct) - 1)
        for x in range(len(self.weights)):
            i = self.struct[x]
            if self.actfunc[x] is activations.sigmoid: # Some rule of thumb I read somewhere, forgot where
                self.weights[x] = np.dot(math.sqrt(1/i), np.random.uniform(low=-1, high=1, size=(self.struct[x + 1], i)))
            elif self.actfunc[x] is activations.relu: # Another rule of thumb I read before promptly forgetting the source
                self.weights[x] = np.dot(math.sqrt(2/i), np.random.uniform(low=-1, high=1, size=(self.struct[x + 1], i)))
            elif self.actfunc[x] is activations.linear: # Uses LeCun Normal
                self.weights[x] = np.random.normal(loc=10e-13, scale=math.sqrt(1/i), size=(self.struct[x + 1], i))
            else:
                self.weights[x] = np.dot(math.sqrt(1/i), np.random.uniform(low=-1, high=1, size=(self.struct[x + 1], i)))
            self.weights[x].astype('float')
        self.biases = [None] * (len(struct) - 1)
        for x in range(len(self.biases)):
            self.biases[x] = np.zeros((self.struct[x + 1], 1))
            self.biases[x].astype('float')

    def addLayer(self, struct, actfunc="sigmoid", input_shape=None):
        if input_shape is not None:
            if len(self.struct) == 0:
                self.struct.append(input_shape)
            elif self.struct[-1] != input_shape:
                warnings.warn("Specified input shape (" + str(input_shape) + ") does not match with previous layer output shape + (" + str(self.struct[-1]) + ").")
        else:
            input_shape = self.struct[-1]
        if isinstance(actfunc, str):
            try:
                exec("activations." + actfunc)
            except:
                warnings.warn("Activation function specified (" + actfunc + ") is not defined.")
            else:
                actfunc = eval("activations." + actfunc)
        self.actfunc.append(actfunc)
        self.struct.append(struct)
        if actfunc is activations.sigmoid: # Some rule of thumb I read somewhere, forgot where
            self.weights.append(np.dot(math.sqrt(1/input_shape), np.random.uniform(low=-1, high=1, size=(struct, input_shape))))
        elif actfunc is activations.relu: # Another rule of thumb I read before promptly forgetting the source
            self.weights.append(np.dot(math.sqrt(2/input_shape), np.random.uniform(low=-1, high=1, size=(struct, input_shape))))
        elif actfunc is activations.linear: # Uses LeCun Normal
            self.weights.append(np.random.normal(loc=10e-13, scale=math.sqrt(1/input_shape), size=(struct, input_shape)))
        else:
            self.weights.append(np.dot(math.sqrt(1/input_shape), np.random.uniform(low=-1, high=1, size=(struct, input_shape))))
        self.weights[-1].astype('float')
        self.biases.append(np.zeros((struct, 1)))
        self.biases[-1].astype('float')


    def feedForward(self, ip, backprop=False):
        ip = np.asarray(ip).flatten()
        ip = np.reshape(ip, (-1, 1))
        if backprop:
            logz = [None] * (len(self.struct) - 1)
        for x in range(len(self.struct) - 1):
            if x == 0:
                food = np.dot(self.weights[x], ip)
            else:
                food = np.dot(self.weights[x], food)
            if backprop:
                logz[x] = np.add(food, self.biases[x])
                logz[x] = logz[x].reshape((1, len(logz[x])))
            food = self.actfunc[x](np.add(food, self.biases[x]))
        if backprop:
            return (food.reshape((len(food),)), logz)
        return food.reshape((len(food),)).tolist()

    def backPropagate(self, ip, output, lf):
        netop, logz = self.feedForward(ip, True)
        output = np.array([output])
        ip = np.asarray(ip)
        delzdela = [None] * (len(self.struct) - 1)
        weightgrad = [None] * (len(self.struct) - 1)
        biasgrad = [None] * (len(self.struct) - 1)
        for x in range(len(self.weights)):
            weightgrad[x] = np.zeros(self.weights[x].shape, dtype=np.float64)
            biasgrad[x] = np.zeros(self.biases[x].shape, dtype=np.float64)
        for x in range(len(self.struct) - 1):
            if x == 0:
                delzdela[-1] = lf(netop, output, df=True)
                loss = lf(netop, output, df=False)
            else:
                delzdela[-(x + 1)] = np.dot(np.multiply(delzdela[-x], self.actfunc[-x](logz[-x], df=True)), self.weights[-x])
        for x in range(len(self.struct) - 1):
            if x == (len(self.struct) - 2):
                intin = ip.reshape((1, -1))
            else:
                intin = self.actfunc[-(x + 2)](logz[-(x + 2)])
            pmat = np.multiply(self.actfunc[-(x + 1)](logz[-(x + 1)], df=True), delzdela[-(x + 1)])
            pmat = pmat.reshape((-1, 1))
            weightgrad[-(x + 1)] = np.dot(pmat, intin)
        for x in range(len(self.struct) - 1):
            tempbias = np.multiply(self.actfunc[-(x + 1)](logz[-(x + 1)], df=True), delzdela[-(x + 1)])
            biasgrad[-(x + 1)] = np.reshape(tempbias, self.biases[-(x + 1)].shape)

        return ([weightgrad, biasgrad], loss)

    def adjustParams(self, gradient, lr, mnp="avg"):
        if mnp == "avg":
            n = len(gradient)
        elif mnp == "sum":
            n = 1
        for a in range(len(gradient)):
            for x in range(len(self.weights)):
                self.weights[x] -= np.dot((lr/n), gradient[a][0][x])
                self.biases[x] -= np.dot((lr/n), gradient[a][1][x])

    def fit(self, inputs, outputs, epochs, batch_size=16, lr=0.1, lf=losses.MSE, verbose=1):
        n_batches = int(len(inputs)/batch_size)
        for x in range(epochs):
            for y in range(n_batches):
                gradient = [None] * batch_size
                for z in range(batch_size):
                    gradient[z], loss = self.backPropagate(np.asarray(inputs[z + (batch_size * y)]).astype('float64').tolist(), np.asarray(outputs[z + (batch_size * y)]).astype('float64').tolist(), lf)
                self.adjustParams(gradient, lr, "avg")
                if verbose == 1:
                    print("Percentage Complete: " + str(round(((x*n_batches) + y + 1) * 100 / (epochs*n_batches), 2)) + "% | Epoch: " + str(x + 1) + " | Loss: " + str(round(loss,4)), end = '\r')
                elif verbose == 2:
                    printProgress(round(((x*n_batches) + y + 1)), (epochs*n_batches))
                elif verbose == 3:
                    printProgress(round(y + 1), n_batches, prefix='Epoch ' + str(x + 1) + '/' + str(epochs) + ':')
            if verbose == 3:
                print("")

    def save(self, name="untitled.aunn"):
        with open(name, 'wb') as f:
            pkl.dump(self, f)

def printProgress(iteration, total, prefix = 'Progress:', suffix = 'Complete', decimals = 1, length = 50, fill = '█'):
    # From https://stackoverflow.com/a/34325723/7296192
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    if iteration == total:
        print()

def shuffleData(inputs, outputs=[]):
    if outputs == []:
        outputs = inputs[1]
        inputs = inputs[0]
    c = list(zip(inputs, outputs))
    random.shuffle(c)
    inputs, outputs = zip(*c)
    return (inputs, outputs)

def loadModel(name="untitled.aunn"):
    with open(name, 'rb') as f:
       model = pkl.load(f)
    return model

def automagic(x, y):
    i, o = len(inputs[0]), len(outputs[0])
    h = (len(i)*2/3) + len(o)
    if (np.asarray(outputs).flatten() >= 0).all() and (np.asarray(outputs).flatten() <= 1).all():
        ot = "sigmoid"
    else:
        ot = "linear"
    if len(outputs) > 128:
        bs = 32
    else:
        bs = 1
    model = aunnl.NeuralNetwork([i, h, o], ["relu", ot])
    model.fit(inputs, outputs, epochs, 3, lr, losses.MSE)
