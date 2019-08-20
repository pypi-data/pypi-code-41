from abc import ABCMeta, abstractmethod


class Callback(metaclass=ABCMeta):

    def __init__(self,
                 monitor: str,
                 mode: str,
                 verbose: bool = False,
                 ):
        self.monitor = monitor
        self.mode = mode
        self.verbose = verbose
        self.previous_value = 0

        self.train_loss = float('inf')
        self.train_accuracy = float('inf')
        self.validation_loss = float('inf')
        self.validation_accuracy = float('inf')

        if self.monitor == 'train_loss' and self.mode == 'max':
            self.train_loss = float('-inf')
        elif self.monitor == 'train_accuracy' and self.mode == 'max':
            self.train_accuracy = float('-inf')
        elif self.monitor == 'validation_loss' and self.mode == 'max':
            self.validation_loss = float('-inf')
        elif self.monitor == 'validation_accuracy' and self.mode == 'max':
            self.validation_accuracy = float('-inf')

    @abstractmethod
    def execute(self, condition_satisfied: bool) -> bool:
        pass

    def callback(self,
                 train_loss: float,
                 train_accuracy: float = 0.0,
                 validation_loss: float = 0.0,
                 validation_accuracy: float = 0.0,
                 ) -> bool:

        condition_satisfied = False

        if self.monitor == 'train_loss':
            if self.mode == 'min' and self.train_loss > train_loss:
                self.previous_value = self.train_loss
                self.train_loss = train_loss
                condition_satisfied = True
            elif self.mode == 'max' and self.train_loss < train_loss:
                self.previous_value = self.train_loss
                self.train_loss = train_loss
                condition_satisfied = True

        elif self.monitor == 'train_accuracy':
            if self.mode == 'min' and self.train_accuracy > train_accuracy:
                self.previous_value = self.train_accuracy
                self.train_accuracy = train_accuracy
                condition_satisfied = True
            elif self.mode == 'max' and self.train_accuracy < train_accuracy:
                self.previous_value = self.train_accuracy
                self.train_accuracy = train_accuracy
                condition_satisfied = True

        elif self.monitor == 'validation_loss':
            if self.mode == 'min' and self.validation_loss > validation_loss:
                self.previous_value = self.validation_loss
                self.validation_loss = validation_loss
                condition_satisfied = True
            elif self.mode == 'max' and self.validation_loss < validation_loss:
                self.previous_value = self.validation_loss
                self.validation_loss = validation_loss
                condition_satisfied = True

        elif self.monitor == 'validation_accuracy':
            if self.mode == 'min' and self.validation_accuracy > validation_accuracy:
                self.previous_value = self.validation_accuracy
                self.validation_accuracy = validation_accuracy
                condition_satisfied = True
            elif self.mode == 'max' and self.validation_accuracy < validation_accuracy:
                self.previous_value = self.validation_accuracy
                self.validation_accuracy = validation_accuracy
                condition_satisfied = True

        return self.execute(condition_satisfied=condition_satisfied)

    def improvement(self):
        if self.monitor == 'train_loss':
            return self.previous_value, self.train_loss
        elif self.monitor == 'train_accuracy':
            return self.previous_value, self.train_accuracy
        elif self.monitor == 'validation_loss':
            return self.previous_value, self.validation_loss
        elif self.monitor == 'validation_accuracy':
            return self.previous_value, self.validation_accuracy


class EarlyStop(Callback):

    def __init__(self,
                 monitor: str,
                 mode: str,
                 patience: int,
                 verbose: bool = False,
                 ):
        Callback.__init__(self,
                          monitor=monitor,
                          mode=mode,
                          verbose=verbose,
                          )
        self.patience = patience
        self.count = 0

    def execute(self, condition_satisfied: bool) -> bool:
        self.count += 1

        if condition_satisfied:
            self.count = 0

        elif self.count == self.patience:
            if self.verbose:
                _, new = self.improvement()
                print('\nEarly stop! ' + self.monitor + ' did not improve from ' + str(round(new, 5)) + ' for ' +
                      str(self.patience) + ' epochs', end='')
            return True

        return False


class ModelCheckpoint(Callback):

    def __init__(self,
                 monitor: str,
                 mode: str,
                 filepath: str,
                 verbose: bool = False,
                 ):
        Callback.__init__(self,
                          monitor=monitor,
                          mode=mode,
                          verbose=verbose,
                          )
        self.filepath = filepath

    def execute(self, condition_satisfied: bool) -> bool:

        if condition_satisfied:
            if self.verbose:
                old, new = self.improvement()
                print('\n' + self.monitor + ' improved from ' + str(round(old, 5)) + ' to ' + str(round(new, 5)) +
                      ', saving model to ' + self.filepath, end='')
            return True

        elif self.verbose:
            old, new = self.improvement()
            print('\n' + self.monitor + ' did not improve from ' + str(round(new, 5)), end='')

        return False




