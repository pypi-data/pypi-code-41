import torch.nn as nn, numpy as np, matplotlib.pyplot as plt
import torch
from .initializers import initializers_dict


loss_dict = {'mse':nn.MSELoss()}

##### functions to implement
# fit, predict, compile (necessary?), save_weights, load_weights

class Sequential():
    """
    Sequential model class.
    """

    def __init__(self):
        """
        init function
        """
        self.model = nn.Sequential()
        self.last_layers_units = 0
        self.layer_iter = 0
        self.is_compiled = False
        self.is_fitted = False
        self.epochs = -1

    def add(self,layer, input_shape = None, layer_name  = None,input_features = None):
        "adds a layer to the model"

        # if first layer, define input shape
        if self.layer_iter == 0:

            if input_shape == None and input_features == None:
                # ValueError should not be used
                raise ValueError("Please Specify input_shape or input_features for first layer!")

            elif input_features == None: # if input_shape given (if both given , shape will be given preference)
                self.last_layers_units = input_shape[0]

            else: # if input_features_given
                self.last_layers_units = input_features

        # if name not specifed, specify your own name which is the iteration number of layer
        if layer_name == None:
            layer_name = str(self.layer_iter)

        # extract activation and layer params
        layer_type, current_layer_param, activation = layer[0], layer[1], layer[2]

        # currently only for Dense and Dropout!!!!
        if layer_type == 'Dense':
            nn_layer = nn.Linear(self.last_layers_units, current_layer_param)
            self.last_layers_units = current_layer_param
        elif layer_type =='Dropout':
            nn_layer = nn.Dropout(current_layer_param)

        self.model.add_module(layer_name,nn_layer)

        # if activation is None, it will be treated as linear activation and no module will be added for activation!
        if activation != None:
            self.layer_iter = self.layer_iter + 1
            activation_layer_name = str(self.layer_iter)
            self.model.add_module(activation_layer_name,activation)

        self.layer_iter = self.layer_iter + 1

    def compile(self,loss,optimizer):
        """
        compiles the model with given loss function and optimizer
        """
        self.optimizer = optimizer[0](self.model.parameters(),lr = optimizer[1],weight_decay = optimizer[2])
        self.loss = loss_dict[loss]
        self.is_compiled = True

    def fit(self,X_train,y_train,epochs,verbose = False,validation_data = None, should_plot_history = False):
        """
        trains the model based on given data. Will show progress based on given parameters
        """

        if self.is_compiled == False:
            raise EnvironmentError("Model is not compiled! Please compile first") # change this value error

        # converting training params to np.float64 dtype
        X_train = X_train.astype(np.float64)
        y_train = y_train.astype(np.float64)

        # converting to Tensors
        X_train, y_train = map(torch.Tensor,[X_train,y_train])

        criterion = self.loss

        if validation_data != None:
            X_test = validation_data[0]
            y_test = validation_data[1]

            # converting testing params to np.float64 dtype
            X_test = X_test.astype(np.float64)
            y_test = y_test.astype(np.float64)

            X_test, y_test = map(torch.Tensor, [X_test, y_test])

        training_losses, val_losses = [], []

        # training
        for epoch in range(epochs):
            # Forward Propagation for training loss
            y_pred = self.model(X_train)

            train_loss = criterion(y_pred, y_train)
            training_losses.append(train_loss)

            if validation_data != None:
                y_val = self.model(X_test)  # for validation
                val_loss = criterion(y_val, y_test)
                val_losses.append(val_loss)

            # print verbose if selected
            if verbose:
                if validation_data == None:
                    print('epoch: ', epoch, 'train_loss: ', train_loss.item())
                else:
                    print('epoch: ', epoch, 'train_loss: ', train_loss.item(), 'val_loss: ', val_loss.item())

            # Zero the gradients
            self.optimizer.zero_grad()

            # perform a backward pass (backpropagation)
            train_loss.backward()

            # Update the parameters
            self.optimizer.step()

        if should_plot_history:
            plt.plot(training_losses, label='training_loss')
            if validation_data!=None:
                plt.plot(val_losses, label='validation_loss')
            plt.ylabel('loss')
            plt.xlabel('number of epochs')
            plt.title('Loss History Visualization')
            plt.legend()
            plt.show()

        # if fit performed successfully, update is_fitted param and set epochs
        self.is_fitted = True
        self.epochs = epochs

    def predict(self,X_test):
        """
        makes predictions
        :param X_test:
        :return:
        """

        # converting X_train and y_train to np.float64 dtype
        X_test = X_test.astype(np.float64)

        X_test = torch.Tensor(X_test)
        predictions = self.model(X_test).detach().numpy()

        return predictions

    def save_weights(self,path):
        """
        saves weights to a .dat file
        """
        torch.save(self.model.state_dict(), path)

    def load_weights(self,path):
        """
        loads weights from a .dat file
        """
        self.model.load_state_dict(torch.load(path))

    def initialize_weights(self, initialization = 'xavier'):
        """
        initializes weights with the given initialization
        """
        self.model.apply(initializers_dict[initialization])

    def summary_detailed(self):
        """
        prints and returns summary (network architecture and hyperparameters) of the model
        """

        # for architecture
        summary_dict = {}
        summary_dict['architecture'] = self.create_architecture_summary()

        # for optimizer and loss info which will be present only if the model has been compiled!
        if self.is_compiled:
            summary_dict['optimizer'] = self.optimizer
            summary_dict['loss'] = str(self.loss)

        # if the model has been fit, number of epochs will be added to the dictionary
        if self.is_fitted:
            summary_dict['epochs'] = self.epochs

        return summary_dict

    def create_architecture_summary(self):
        """
        creates summary of model's architecture in a neat way
        currently only works for linear,dropout and relu layers
        """

        architecture_summary = []

        # recording input size
        input_size = self.model[0].in_features
        architecture_summary.append("INPUT (" + str(input_size) + ")")

        # iterating through each layer
        for each_layer in self.model:

            if type(each_layer) == nn.modules.activation.ReLU:
                architecture_summary .append("RELU")
            elif type(each_layer) == nn.modules.dropout.Dropout:
                architecture_summary .append("DROPOUT (" + str(each_layer.p) + ")")
            else:
                architecture_summary .append("LINEAR (" + str(each_layer.out_features) + ")")

        return architecture_summary