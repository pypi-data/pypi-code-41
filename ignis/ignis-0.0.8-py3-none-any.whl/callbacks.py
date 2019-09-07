from abc import ABCMeta, abstractmethod


class Callback(metaclass=ABCMeta):

    def __init__(self,
                 monitor: str,
                 ):
        self.monitor = monitor
        self.previous_value = 0

        self.train_loss = float('inf')
        self.validation_loss = float('inf')

    @abstractmethod
    def execute(self, condition_satisfied: bool) -> bool:
        pass

    def callback(self,
                 train_loss: float,
                 validation_loss: float = 0.0,
                 ) -> bool:

        condition_satisfied = False

        if self.monitor == 'train_loss':
            if self.train_loss > train_loss:
                self.previous_value = self.train_loss
                self.train_loss = train_loss
                condition_satisfied = True

        elif self.monitor == 'validation_loss':
            if self.validation_loss > validation_loss:
                self.previous_value = self.validation_loss
                self.validation_loss = validation_loss
                condition_satisfied = True

        return self.execute(condition_satisfied=condition_satisfied)

    def improvement(self):
        if self.monitor == 'train_loss':
            return self.previous_value, self.train_loss
        elif self.monitor == 'validation_loss':
            return self.previous_value, self.validation_loss


class EarlyStop(Callback):

    def __init__(self,
                 monitor: str,
                 patience: int,
                 ):
        Callback.__init__(self,
                          monitor=monitor,
                          )
        self.patience = patience
        self.count = 0

    def execute(self, condition_satisfied: bool) -> bool:
        self.count += 1
        if condition_satisfied:
            self.count = 0
        elif self.count == self.patience:
            return True

        return False


class ModelCheckpoint(Callback):

    def __init__(self,
                 monitor: str,
                 filepath: str,
                 ):
        Callback.__init__(self,
                          monitor=monitor,
                          )
        self.filepath = filepath

    def execute(self, condition_satisfied: bool) -> bool:

        if condition_satisfied:
            return True

        return False

