import torch
from torch.nn import CrossEntropyLoss


DTYPE = torch.FloatTensor

class Layer:
    def __init__(self, size_in, size_out, activation):
        self.weights = torch.randn(size_in, size_out, type=DTYPE, requires_grad=True)
        self.bias = torch.randn(1, size_out, type=DTYPE, requires_grad=True)
        self.activation = activation

    def __call__(self, z_in):
        return self.activation(self.weights @ z_in + self.bias)

    def GetVariables(self):
        return self.weights, self.bias


class LSTM:
    def __init__(self, rate, input_size, short_size, long_size, output_size):
        self.input_size = input_size
        self.short_size = short_size
        self.long_size = long_size
        self.inner_size = self.input_size + self.short_size
        self.output_size = output_size

        self.forget_gate = Layer(self.inner_size, self.long_size, torch.sigmoid)

        self.memory_layer = Layer(self.inner_size, self.long_size, lambda x: x)
        self.memory_gate = Layer(self.inner_size, self.long_size, torch.sigmoid)

        self.recall_layer = Layer(self.long_size, self.short_size, torch.tanh)
        self.recall_gate = Layer(self.inner_size, self.short_size, torch.sigmoid)

        self.output_layer = Layer(self.short_size, self.output_size, lambda x: x)

        self.optimizer = torch.optim.Adam(self.GetVariables(), lr=rate)
        self.loss_func = torch.nn.CrossEntropyLoss()

    def GetVariables(self):
        self.variables = []
        for name in dir(self):
            obj = getattr(self, name)
            if type(obj) == Layer:
                self.variables.extend(obj.GetVariables())
        return self.variables

    def Forward(self, x, constant):
        mem_short = torch.zeros(1, self.short_size)
        mem_long = torch.zeros(1, self.long_size)

        out_list = []

        for i in range(x.shape[0] - 1):
            inner = torch.cat((x[[i], :], mem_short, constant), dim=1)
            mem_long = mem_long * self.forget_gate(inner)
            mem_long = mem_long + self.memory_gate(inner) * self.memory_layer(inner)
            mem_short = self.recall_gate(inner) * self.recall_layer(mem_long)
            out = self.output_layer(mem_short)
            out_list.append(out)

        return torch.cat(out_list)

    def Backward(self, y_hat, y):
        loss = self.loss_func(y_hat, y)
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()
        return loss.detach()

    def Train(self, x, constant, y):
        y_hat = self.Forward(x, constant)
        loss = self.Backward(y_hat, y)
        return y_hat.detach().cpu().numpy(), loss.detach().cpu().numpy()

    def Generate(self, constant, start_token, stop_token, factor=0.001, ):
        mem_short = torch.randn(1, self.short_size) * factor
        mem_long = torch.randn(1, self.long_size) * factor

        out = ''
        out_list = []
        while out != stop_token:
            inner = torch.cat((start_token, mem_short, constant), dim=1)
            mem_long = mem_long * self.forget_gate(inner)
            mem_long = mem_long + self.memory_gate(inner) * self.memory_layer(inner)
            mem_short = self.recall_gate(inner) * self.recall_layer(mem_long)
            out = self.output_layer(mem_short)
            out_list.append(out)
        return out_list





