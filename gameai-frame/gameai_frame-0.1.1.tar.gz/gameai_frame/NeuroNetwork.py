from . import Matrix as Mt
import tkinter.filedialog
import time
SAVE_FILE_PATH = "save.txt"
class NeuralNet(object):
    def __init__(self, input_size, hidden_size, output_size, hidden_layer_num):
        #
        self.save_path = SAVE_FILE_PATH
        #
        self.iNodes = input_size#输入层节点数
        self.hNodes = hidden_size#每个隐藏层的节点数
        self.hLayers = hidden_layer_num#隐藏层数
        self.oNodes = output_size
        self.weights = []
        self.weights.append(Mt.Matrix(self.hNodes, self.iNodes+1))
        for i in range(self.hLayers):
            self.weights.append(Mt.Matrix(self.hNodes, self.hNodes+1))
        self.weights.append(Mt.Matrix(self.oNodes, self.hNodes+1))
        for i in range(len(self.weights)):
            self.weights[i].randomize()
        return
    #改变自身权重
    def mutate(self, mutate_rate):
        for i in range(len(self.weights)):
            self.weights[i].mutate(mutate_rate)
        return
    #获得输出层节点
    #inputs : 输入节点, 限定 : len(inputs) == self.iNodes
    #return : 返回对应的输出节点的值
    def output(self, inputs : list):
        in_mat = Mt.Matrix.fromArray(inputs)
        cur_bias = in_mat.addBias()
        for i in range(self.hLayers):
            hidden_ip = self.weights[i].dot(cur_bias)
            hidden_op = hidden_ip.activate()
            cur_bias = hidden_op.addBias()
        output_ip = self.weights[-1].dot(cur_bias)
        output = output_ip.activate()
        return output.toArray()
    #杂交, 改变权重
    #return : 返回杂交的子NeuralNet
    def crossover(self, partner):
        rst = NeuralNet(self.iNodes, self.hNodes, self.oNodes, self.hLayers)
        for i in range(len(self.weights)):
            rst.weights[i] = self.weights[i].crossover(partner.weights[i])
        return rst
    def clone(self):
        rst = NeuralNet(self.iNodes, self.hNodes, self.oNodes, self.hLayers)
        for i in range(len(self.weights)):
            rst.weights[i] = self.weights[i]
        return rst
    #从外部载入网络的权重
    def load_weights(self, weight : list):
        for i in range(len(self.weights)):
            self.weights[i] = weight[i]
        return
    #get weights
    def pull_weights(self):
        rst = []
        for i in range(len(self.weights)):
            rst.append(self.weights[i])
        return rst
    #use fixed file name
    def save(self):
        if self.save_path == "":
            return
        with open(self.save_path, "w") as save:
            save.write("{},{}\n".format(self.iNodes, self.oNodes))
            save.write("{},{}\n".format(self.hLayers, self.hNodes))
            #write weight_ih(self.hNodes, self.iNodes+1)
            for n in range(len(self.weights)):
                for i in range(self.weights[n].Rows):
                    for j in range(self.weights[n].Cols):
                        save.write("{},".format(self.weights[n].Vals[i][j]))
                    save.write("\n")
        return
    def save_as(self):
        root = tkinter.Tk()
        root.withdraw()
        self.save_path = tkinter.filedialog.askopenfilename()
        self.save()
        return
    #use fixed file name
    #assert file format
    def load(self):
        root = tkinter.Tk()
        root.withdraw()
        self.save_path = tkinter.filedialog.askopenfilename()
        if self.save_path == "":
            return
        with open(self.save_path, "r") as save:
            line = save.readline()
            vals = line.split(",")
            self.iNodes = int(vals[0])
            self.oNodes = int(vals[1])
            line = save.readline()
            vals = line.split(",")
            self.hLayers = int(vals[0])
            self.hNodes = int(vals[1])
            #valid weights
            self.weights = []
            self.weights.append(Mt.Matrix(self.hNodes, self.iNodes+1))
            for i in range(self.hLayers):
                self.weights.append(Mt.Matrix(self.hNodes, self.hNodes+1))
            self.weights.append(Mt.Matrix(self.oNodes, self.hNodes+1))
            #read weights
            for n in range(len(self.weights)):
                for i in range(self.weights[n].Rows):
                    line = save.readline()
                    vals = line.split(",")
                    for j in range(self.weights[n].Cols):
                        self.weights[n].Vals[i][j] = float(vals[j])
        return