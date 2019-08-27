import torch
from torch.utils import data
from .callbacks import EarlyStop, ModelCheckpoint
from .datasets import Dataset

name = 'ignis'


def pack_data(x, y, validation_split, batch_size, num_workers):
    dataset = Dataset(x=x, y=y)

    x_size = len(x)
    validation_size = int(x_size * validation_split)
    train_size = x_size - validation_size
    train_set, validation_set = data.random_split(dataset=dataset, lengths=(train_size, validation_size))

    train_loader = data.DataLoader(
        dataset=train_set,
        batch_size=batch_size,
        num_workers=num_workers,
    )
    validation_loader = data.DataLoader(
        dataset=validation_set,
        batch_size=batch_size,
        num_workers=num_workers,
    )

    return train_loader, train_size, validation_loader, validation_size


def train(model, optimizer, loss_fn, loader, size, verbose):
    train_points = 0
    train_loss = 0
    train_epoch_loss = 0
    for x, y in loader:

        y_pred = model(x)
        optimizer.zero_grad()
        loss = loss_fn(y_pred, y)
        loss.backward()
        optimizer.step()

        train_loss += loss.item()
        train_points += y.shape[0]
        train_epoch_loss = train_loss/train_points

        if verbose:
            print('\rTrain ' + str(train_points) + '/' + str(size) + ' - loss: ' +
                  str(round(train_epoch_loss, 5)), end='')

    return train_epoch_loss


def validate(model, loss_fn, loader, size, verbose):
    validation_points = 0
    validation_loss = 0
    validation_epoch_loss = 0

    model.eval()
    with torch.no_grad():
        for x, y in loader:

            y_pred = model(x)
            loss = loss_fn(y_pred, y)

            validation_loss += loss.item()
            validation_points += y.shape[0]
            validation_epoch_loss = validation_loss / validation_points

            if verbose:
                print('\rValidate ' + str(validation_points) + '/' + str(size) + ' - loss: ' +
                      str(round(validation_epoch_loss, 5)), end='')
    model.train()

    return validation_epoch_loss


def fit(x,
        y,
        model,
        loss_fn,
        optimizer,
        epoch,
        validation_split=0,
        batch_size=16,
        num_workers=6,
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
        num_workers=num_workers,
    )

    for i in range(1, epoch+1):

        if verbose:
            print('Epoch: ' + str(i) + '/' + str(epoch))

        train_epoch_loss = train(
            model=model,
            optimizer=optimizer,
            loss_fn=loss_fn,
            loader=train_loader,
            size=train_size,
            verbose=verbose,
        )

        validation_epoch_loss = 0
        if validation_split > 0:
            if verbose:
                print()

            validation_epoch_loss = validate(
                model=model,
                loss_fn=loss_fn,
                loader=validation_loader,
                size=validation_size,
                verbose=verbose,
            )

        stop = False
        for callback in callbacks:
            execute = callback.callback(
                train_loss=train_epoch_loss,
                validation_loss=validation_epoch_loss,
            )

            if isinstance(callback, EarlyStop):
                if execute:
                    stop = True
                    if verbose:
                        _, new = callback.improvement()
                        print('\nEarly stop! ' + callback.monitor + ' did not improve from ' + str(round(new, 5)) +
                              ' for ' + str(callback.patience) + ' epochs', end='')

            elif isinstance(callback, ModelCheckpoint):
                if execute:
                    torch.save(model, callback.filepath)
                    if verbose:
                        old, new = callback.improvement()
                        print('\n' + callback.monitor + ' improved from ' + str(round(old, 5)) + ' to ' +
                              str(round(new, 5)) + ', saving model to ' + callback.filepath, end='')
                elif verbose:
                    old, new = callback.improvement()
                    print('\n' + callback.monitor + ' did not improve from ' + str(round(new, 5)), end='')

        if stop:
            break

        if verbose:
            print('\n')

    if verbose:
        print()
