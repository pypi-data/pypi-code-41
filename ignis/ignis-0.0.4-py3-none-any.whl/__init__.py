import torch
from torch.utils import data
from .callbacks import EarlyStop, ModelCheckpoint
from .datasets import Dataset

name = 'ignis'


def pack_data(x, y, validation_split, batch_size):
    dataset = Dataset(x=x, y=y)

    x_size = len(x)
    validation_size = int(x_size * validation_split)
    train_size = x_size - validation_size
    train_set, validation_set = data.random_split(dataset=dataset, lengths=(train_size, validation_size))

    train_loader = data.DataLoader(
        dataset=train_set,
        batch_size=batch_size,
        num_workers=6,
    )
    validation_loader = data.DataLoader(
        dataset=validation_set,
        batch_size=batch_size,
        num_workers=6,
    )

    return train_loader, train_size, validation_loader, validation_size


def fit(x,
        y,
        model,
        loss_fn,
        optimizer,
        epoch,
        validation_split=0,
        batch_size=16,
        callbacks=None,
        verbose=True,
        ):
    if callbacks is None:
        callbacks = []

    train_loader, train_size, validation_loader, validation_size = pack_data(
        x=x,
        y=y,
        validation_split=validation_split,
        batch_size=batch_size,
    )

    for i in range(1, epoch+1):

        if verbose:
            print('Epoch: ' + str(i) + '/' + str(epoch))

        train_points = 0
        train_loss = 0
        train_accuracy = 0
        train_epoch_loss = 0
        for x, y in train_loader:

            y_pred = model(x)
            optimizer.zero_grad()
            loss = loss_fn(y_pred, y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item()
            train_points += y.shape[0]
            train_epoch_loss = train_loss/train_points

            if verbose:
                print('\rTrain ' + str(train_points) + '/' + str(train_size) + ' - loss: ' +
                      str(round(train_epoch_loss, 5)), end='')

        validation_points = 0
        validation_loss = 0
        validation_accuracy = 0
        validation_epoch_loss = 0
        if validation_split > 0:
            if verbose:
                print()

            model.eval()
            with torch.no_grad():
                for x, y in validation_loader:

                    y_pred = model(x)
                    loss = loss_fn(y_pred, y)

                    validation_loss += loss.item()
                    validation_points += y.shape[0]
                    validation_epoch_loss = validation_loss / validation_points

                    if verbose:
                        print('\rValidate ' + str(validation_points) + '/' + str(validation_size) + ' - loss: ' +
                              str(round(validation_epoch_loss, 5)), end='')
            model.train()

        stop = False
        for callback in callbacks:
            execute = callback.callback(
                train_loss=train_epoch_loss,
                train_accuracy=train_accuracy,
                validation_loss=validation_epoch_loss,
                validation_accuracy=validation_accuracy,
            )

            if isinstance(callback, EarlyStop) and execute:
                stop = True
            elif isinstance(callback, ModelCheckpoint) and execute:
                torch.save(model, callback.filepath)

        if stop:
            break

        if verbose:
            print('\n')

    if verbose:
        print()
