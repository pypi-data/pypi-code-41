import torch.nn as nn



# for xavier initialization
# initialization function, first checks the module type,
# then applies the desired changes to the weights
def xavier_init(m):
    if type(m) == nn.Linear:
        nn.init.xavier_uniform_(m.weight)



initializers_dict = {'xavier' : xavier_init}
