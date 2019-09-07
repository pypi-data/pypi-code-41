import torch
from .callbacks import EarlyStop, ModelCheckpoint


def fit(train_loader,
        validation_loader,
        model,
        loss_fn,
        optimizer,
        epochs=100,
        callbacks=None,
        verbose=True,
        ):
    if callbacks is None:
        callbacks = []

    for i in range(1, epochs+1):

        if verbose:
            print('Epoch: ' + str(i) + '/' + str(epochs))

        train_points = 0
        train_loss = 0
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
                print('\rTrain ' + str(train_points) + '/' + str(train_points) + ' - loss: ' +
                      str(round(train_epoch_loss, 5)), end='')

        validation_epoch_loss = 0
        if len(validation_loader) > 0:
            if verbose:
                print()

            validation_points = 0
            validation_loss = 0
            validation_epoch_loss = 0
            model.eval()
            with torch.no_grad():
                for x, y in validation_loader:
                    y_pred = model(x)
                    loss = loss_fn(y_pred, y)

                    validation_loss += loss.item()
                    validation_points += y.shape[0]
                    validation_epoch_loss = validation_loss / validation_points

                    if verbose:
                        print('\rValidate ' + str(validation_points) + '/' + str(validation_points) + ' - loss: ' +
                              str(round(validation_epoch_loss, 5)), end='')
            model.train()

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
