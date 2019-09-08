
import matplotlib.pyplot as plt

class history():
    '''history of fit method'''

    def __init__(self,training_loss,validation_losses = []):
        self.training_losses = training_loss
        self.validation_losses = validation_losses

    def plot(self,show = False):
        '''
        plots the history
        :param show:
        :return:
        '''

        fig = plt.figure()
        _ = plt.plot(self.training_losses, label='training_loss')
        if self.validation_losses != []:
            _ = plt.plot(self.validation_losses, label='validation_loss')
        _ = plt.ylabel('loss')
        _ = plt.xlabel('number of epochs')
        _ = plt.title('Loss History Visualization')
        _ = plt.legend()

        if show:
            plt.show()
            return

        return fig