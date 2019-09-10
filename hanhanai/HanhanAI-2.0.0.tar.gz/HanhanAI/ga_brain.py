# ======================================================================================================================
# ================================================Brain Part============================================================
# ======================================================================================================================
"""
作者：赵士陆
创建时间：2019.9.2
最后一次修改时间：2019.9.10

"""
import numpy as np


class Network:
    def __init__(
            self,
            size_inputlayer=0,
            size_hiddenlayer_1=0,
            size_hiddenlayer_2=0,
            size_outputlayer=0
                 ):
        # define the layers of the nets
        self.layer_input = size_inputlayer
        self.layer_hidden_1 = size_hiddenlayer_1
        self.layer_hidden_2 = size_hiddenlayer_2
        self.layer_output = size_outputlayer

        self.weight_input = 2*np.random.rand(size_inputlayer, size_hiddenlayer_1) - 1
        self.weight_hidden_1 = 2*np.random.rand(size_hiddenlayer_1, size_hiddenlayer_2) - 1
        self.weight_hidden_2 = 2*np.random.rand(size_hiddenlayer_2, size_outputlayer) - 1

        self.weight_input_binary = []
        self.weight_hidden_1_binary = []
        self.weight_hidden_2_binary = []

        self.bias_input = np.random.rand(size_hiddenlayer_1)
        self.bias_hidden_1 = np.random.rand(size_hiddenlayer_2)
        self.bias_hidden_2 = np.random.rand(size_outputlayer)

        self.bias_input_binary = []
        self.bias_hidden_1_binary = []
        self.bias_hidden_2_binary = []

        # define the default parameters of the nets
        self.mutate_freq = 0.01
        self.final_mutate_freq = 0.001
        self.mutate_freq_decay_rate = 0.7
        self.mutate_freq_decay_step = 1000
        self.mutate_degree_per_gene = 3

        self.generation = 1

        self.evaluate_score = 0
        self.chosen_rate = 0
        self.accumulative_rate = 0

    def decrease_mutate_freq(self):     # decrease the mutate frequency
        if self.mutate_freq > self.final_mutate_freq:
            self.mutate_freq = self.mutate_freq*self.mutate_freq_decay_rate ^ \
                               (self.mutate_freq_decay_step/self.generation)

    def activationFunc(self, name, x):  # activation
        if name == 'relu':
            return np.maximum(0, x)
        elif name == 'sigmoid':
            y = 1/(1 + np.exp(-x))
            return y
        elif name == 'tanh':
            y = (np.exp(x) - np.exp(-x))/(np.exp(x) + np.exp(-x))
            return y

    def run(self, input_vector):        # predict the result based on the input

        out_input = np.dot(input_vector, self.weight_input) + self.bias_input
        activated_input = self.activationFunc('relu', out_input)

        out_hidden_1 = np.dot(activated_input, self.weight_hidden_1)
        activated_hidden_1 = self.activationFunc('relu', out_hidden_1)

        out_hidden_2 = np.dot(activated_hidden_1, self.weight_hidden_2)
        activated_hidden_2 = self.activationFunc('tanh', out_hidden_2)

        out_result = activated_hidden_2
        # print(out_result)
        return out_result


def cross(network_1, network_2):        # cross two nets to generate the next generation
    print('\nGeneration ', network_1.generation, ' Crossing...\n')
    crossed_network = Network(
        network_1.layer_input,
        network_1.layer_hidden_1,
        network_1.layer_hidden_2,
        network_1.layer_output
                              )

    crossed_network.generation = network_1.generation + 1

    # cross weight
    weight_input_vec_1 = matrixToVector(network_1.weight_input)         # weight matrix --> weight vector
    weight_input_vec_2 = matrixToVector(network_2.weight_input)         # then cross
    weight_input_crossed_vec = []
    for i in range(len(weight_input_vec_1)):
        if np.random.rand() < 0.5:
            weight_input_crossed_vec.append(weight_input_vec_1[i])
        else:
            weight_input_crossed_vec.append(weight_input_vec_2[i])

    weight_hidden_1_vec_1 = matrixToVector(network_1.weight_hidden_1)
    weight_hidden_1_vec_2 = matrixToVector(network_2.weight_hidden_1)
    weight_hidden_1_crossed_vec = []
    for i in range(len(weight_hidden_1_vec_1)):
        if np.random.rand() < 0.5:
            weight_hidden_1_crossed_vec.append(weight_hidden_1_vec_1[i])
        else:
            weight_hidden_1_crossed_vec.append(weight_hidden_1_vec_2[i])

    weight_hidden_2_vec_1 = matrixToVector(network_1.weight_hidden_2)
    weight_hidden_2_vec_2 = matrixToVector(network_2.weight_hidden_2)
    weight_hidden_2_crossed_vec = []
    for i in range(len(weight_hidden_2_vec_1)):
        if np.random.rand() < 0.5:
            weight_hidden_2_crossed_vec.append(weight_hidden_2_vec_1[i])
        else:
            weight_hidden_2_crossed_vec.append(weight_hidden_2_vec_2[i])

    # cross bias
    for i in range(len(crossed_network.bias_input)):
        if np.random.rand() < 0.5:
            crossed_network.bias_input[i] = network_1.bias_input[i]
        else:
            crossed_network.bias_input[i] = network_2.bias_input[i]

    for i in range(len(crossed_network.bias_hidden_1)):
        if np.random.rand() < 0.5:
            crossed_network.bias_hidden_1[i] = network_1.bias_hidden_1[i]
        else:
            crossed_network.bias_hidden_1[i] = network_2.bias_hidden_1[i]

    for i in range(len(crossed_network.bias_hidden_2)):
        if np.random.rand() < 0.5:
            crossed_network.bias_hidden_2[i] = network_1.bias_hidden_2[i]
        else:
            crossed_network.bias_hidden_2[i] = network_2.bias_hidden_2[i]

    print('Cross complete.\n')

    return crossed_network


def mutate(origin_network):         # the next generation mutate their gene
    print('Mutate frequency is ', origin_network.mutate_freq,
          '\nGeneration ', origin_network.generation, ' Mutating...\n')

    # mutate weight
    weight_input_vec = matrixToVector(origin_network.weight_input)
    for i in range(len(weight_input_vec)):
        origin_network.weight_input_binary.append(decToBinary(weight_input_vec[i]))
        for j in range(len(origin_network.weight_input_binary[i])):                     # weight matrix-->weight vector
            if np.random.rand() < origin_network.mutate_freq:                           # trans values in weight vector
                if origin_network.weight_input_binary[i][j] == '0':                     # from Decimal to binary
                    origin_network.weight_input_binary[i] = \
                        replaceChar(origin_network.weight_input_binary[i], '1', j)
                elif origin_network.weight_input_binary[i][j] == '1':
                    origin_network.weight_input_binary[i] = \
                        replaceChar(origin_network.weight_input_binary[i], '0', j)
    for i in range(len(weight_input_vec)):
        weight_input_vec[i] = binaryToDec(origin_network.weight_input_binary[i])
        origin_network.weight_input = vectorToMatrix(weight_input_vec,
                                                     origin_network.layer_input,
                                                     origin_network.layer_hidden_1)

    weight_hidden_1_vec = matrixToVector(origin_network.weight_hidden_1)
    for i in range(len(weight_hidden_1_vec)):
        origin_network.weight_hidden_1_binary.append(decToBinary(weight_hidden_1_vec[i]))
        for j in range(len(origin_network.weight_hidden_1_binary[i])):
            if np.random.rand() < origin_network.mutate_freq:
                if origin_network.weight_hidden_1_binary[i][j] == '0':
                    origin_network.weight_hidden_1_binary[i] = \
                        replaceChar(origin_network.weight_hidden_1_binary[i], '1', j)
                elif origin_network.weight_hidden_1_binary[i][j] == '1':
                    origin_network.weight_hidden_1_binary[i] = \
                        replaceChar(origin_network.weight_hidden_1_binary[i], '0', j)
    for i in range(len(weight_hidden_1_vec)):
        weight_hidden_1_vec[i] = binaryToDec(origin_network.weight_hidden_1_binary[i])
        origin_network.weight_hidden_1 = vectorToMatrix(weight_hidden_1_vec,
                                                        origin_network.layer_hidden_1,
                                                        origin_network.layer_hidden_2
                                                        )

    weight_hidden_2_vec = matrixToVector(origin_network.weight_hidden_2)
    for i in range(len(weight_hidden_2_vec)):
        origin_network.weight_hidden_2_binary.append(decToBinary(weight_hidden_2_vec[i]))
        for j in range(len(origin_network.weight_hidden_2_binary[i])):
            if np.random.rand() < origin_network.mutate_freq:
                if origin_network.weight_hidden_2_binary[i][j] == '0':
                    origin_network.weight_hidden_2_binary[i] = \
                        replaceChar(origin_network.weight_hidden_2_binary[i], '1', j)
                elif origin_network.weight_hidden_2_binary[i][j] == '1':
                    origin_network.weight_hidden_2_binary[i] = \
                        replaceChar(origin_network.weight_hidden_2_binary[i], '0', j)
    for i in range(len(weight_hidden_2_vec)):
        weight_hidden_2_vec[i] = binaryToDec(origin_network.weight_hidden_2_binary[i])
        origin_network.weight_hidden_2 = vectorToMatrix(weight_hidden_2_vec,
                                                        origin_network.layer_hidden_2,
                                                        origin_network.layer_output
                                                        )

    # mutate bias
    for i in range(len(origin_network.bias_input)):
        origin_network.bias_input_binary.append(decToBinary(origin_network.bias_input[i]))
        for j in range(len(origin_network.bias_input_binary[i])):
            if np.random.rand() < origin_network.mutate_freq:
                if origin_network.bias_input_binary[i][j] == '0':
                    origin_network.bias_input_binary[i] = \
                        replaceChar(origin_network.bias_input_binary[i], '1', j)
                elif origin_network.bias_input_binary[i][j] == '1':
                    origin_network.bias_input_binary[i] = \
                        replaceChar(origin_network.bias_input_binary[i], '0', j)
    for i in range(len(origin_network.bias_input)):
        origin_network.bias_input[i] = binaryToDec(origin_network.bias_input_binary[i])

    for i in range(len(origin_network.bias_hidden_1)):
        origin_network.bias_hidden_1_binary.append(decToBinary(origin_network.bias_hidden_1[i]))
        for j in range(len(origin_network.bias_hidden_1_binary[i])):
            if np.random.rand() < origin_network.mutate_freq:
                if origin_network.bias_hidden_1_binary[i][j] == '0':
                    origin_network.bias_hidden_1_binary[i] = \
                        replaceChar(origin_network.bias_hidden_1_binary[i], '1', j)
                elif origin_network.bias_hidden_1_binary[i][j] == '1':
                    origin_network.bias_hidden_1_binary[i] = \
                        replaceChar(origin_network.bias_hidden_1_binary[i], '0', j)
    for i in range(len(origin_network.bias_hidden_1)):
        origin_network.bias_hidden_1[i] = binaryToDec(origin_network.bias_hidden_1_binary[i])

    for i in range(len(origin_network.bias_hidden_2)):
        origin_network.bias_hidden_2_binary.append(decToBinary(origin_network.bias_hidden_2[i]))
        for j in range(len(origin_network.bias_hidden_2_binary[i])):
            if np.random.rand() < origin_network.mutate_freq:
                if origin_network.bias_hidden_2_binary[i][j] == '0':
                    origin_network.bias_hidden_2_binary[i] = \
                        replaceChar(origin_network.bias_hidden_2_binary[i], '1', j)
                elif origin_network.bias_hidden_2_binary[i][j] == '1':
                    origin_network.bias_hidden_2_binary[i] = \
                        replaceChar(origin_network.bias_hidden_2_binary[i], '0', j)
    for i in range(len(origin_network.bias_hidden_2)):
        origin_network.bias_hidden_2[i] = binaryToDec(origin_network.bias_hidden_2_binary[i])

    # origin_network.mutate_decrease()

    print('Mutation complete.\n')

    return origin_network


# belows are several tool functions.
def decToBinary(dec_num):
    float1_num = (100000000) * dec_num
    int1_num = int(float1_num)
    bin_num = bin(int1_num).replace('0b', '')
    return bin_num


def binaryToDec(bin_num):
    int2_num = int(bin_num, 2)
    float2_num = float(int2_num)
    dec2_num = float2_num / (100000000)
    return dec2_num


def matrixToVector(mat):
    vec = mat.flatten()
    return vec


def vectorToMatrix(vec, column, row):
    mat = vec.reshape(column, row)
    return mat


def replaceChar(string, char, index):
    string = list(string)
    string[index] = char
    return ''.join(string)




