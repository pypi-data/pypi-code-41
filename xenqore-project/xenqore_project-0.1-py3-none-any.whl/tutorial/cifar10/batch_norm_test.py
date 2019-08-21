import xenqore as xq
import numpy as np
import tensorflow as tf



### networks parameter setting
network_config = xq.utils.NetworkConfig()
layers_config = xq.utils.layers_config()
activations_config = xq.utils.activations_config()


(x_train, y_train), (x_valid, y_valid) = tf.keras.datasets.cifar10.load_data()

tr_dataset = tf.data.Dataset.from_tensor_slices((x_train, y_train))
tr_dataset = tr_dataset.batch(network_config.batch_size).repeat().shuffle(10000)
va_dataset = tf.data.Dataset.from_tensor_slices((x_valid, y_valid))
va_dataset = va_dataset.batch(network_config.batch_size).repeat()


model = xq.apps.VGGNet7(mode=0, layer_config=layers_config, act_config=activations_config, classes=network_config.classes)

model.summary()
#transfer_model.summary()




model.compile(
    #optimizer = tf.keras.optimizers.Adam(lr=n_config.initial_lr),
    #optimizer = tf.keras.optimizers.Adam(lr=n_config.initial_lr, decay=n_config.var_decay),
    optimizer = tf.keras.optimizers.Nadam(lr=network_config.initial_lr),
    #loss = tf.keras.losses.CategoricalCrossentropy(),
    loss = tf.keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"]
)


def lr_schedule(epoch, lr):
    if epoch < 150:
        return network_config.initial_lr * 0.1 ** (epoch // 50)
    else:
        if epoch % 5 == 0:
            lr = lr * 0.1
            return lr
        return lr


callbacks = tf.keras.callbacks.ModelCheckpoint(
    filepath='app_new_result/mymodel_{epoch}.h5',
    # Path where to save the model
    # The two parameters below mean that we will overwrite
    # the current checkpoint if and only if
    # the `val_loss` score has improved.
    save_best_only=True,
    #save_weights_only=True,
    monitor='val_accuracy',
    #mode='max',  
    verbose=1)

tensorboard_cbk = tf.keras.callbacks.TensorBoard(
    log_dir='app_new_result',
    histogram_freq=1,  # How often to log histogram visualizations
    embeddings_freq=0,  # How often to log embedding visualizations
    update_freq='epoch')  # How often to write logs (default: once per epoch)


trained_model = model.fit(
    tr_dataset,
    epochs=network_config.epochs,
    steps_per_epoch=x_train.shape[0] // network_config.batch_size,
    validation_data=va_dataset,
    validation_steps=x_valid.shape[0] // network_config.batch_size,
    verbose=1,
    #callbacks=[tf.keras.callbacks.LearningRateScheduler(lr_schedule)]
    #callbacks=[callbacks, tensorboard_cbk]
    callbacks=[callbacks, tensorboard_cbk, tf.keras.callbacks.LearningRateScheduler(lr_schedule, verbose=1)]
)



