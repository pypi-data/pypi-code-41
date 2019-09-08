
import torch.optim as optim

# optimizers
optimizers_dict = {'Adadelta': optim.Adadelta, 'Adagrad': optim.Adagrad, 'Adam': optim.Adam}


def Adadelta(lr = 1, weight_decay = 0):
    return optimizers_dict['Adadelta'], lr, weight_decay

def Adagrad(lr = 0.01, weight_decay = 0):
    return optimizers_dict['Adagrad'], lr, weight_decay

def Adam(lr = 0.001, weight_decay = 0):
    return optimizers_dict['Adam'],lr, weight_decay