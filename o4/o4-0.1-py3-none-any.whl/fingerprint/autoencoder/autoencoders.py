from keras.layers import Input, Dense
from keras.models import Model, load_model
from keras import regularizers
from keras.layers import Input, Dense, Conv2D, MaxPooling2D, UpSampling2D
from keras.models import Model
from keras import backend as K
import numpy as np
from keras.callbacks import TensorBoard


class Autoencoder():
  def __init__(self, load=True, x_train=None, x_test=None):
    self.set_model(loaded=load, x_train=x_train, x_test=x_test)

  def set_model(self, loaded=False, x_train=None, x_test=None):
    # this is the size of our encoded representations
    encoding_dim = (4, 4, 8)

    input_img = Input(shape=(28, 28, 1))  # adapt this if using `channels_first` image data format

    x = Conv2D(16, (3, 3), activation='relu', padding='same')(input_img)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    x = MaxPooling2D((2, 2), padding='same')(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    encoded = MaxPooling2D((2, 2), padding='same')(x)

    # at this point the representation is (4, 4, 8) i.e. 128-dimensional

    x = Conv2D(8, (3, 3), activation='relu', padding='same')(encoded)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(8, (3, 3), activation='relu', padding='same')(x)
    x = UpSampling2D((2, 2))(x)
    x = Conv2D(16, (3, 3), activation='relu')(x)
    x = UpSampling2D((2, 2))(x)
    decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)

    autoencoder = Model(input_img, decoded)
    autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')

    # create a placeholder for an encoded (32-dimensional) input
    encoded_input = Input(shape=(4, 4, 8,))

    decoder = None

    if loaded:
      self.autoencoder = load_model('autoencoder/my_model.h5')
    else:
      self.autoencoder = self.train(x_train, x_test)

    self.encoder = self.get_encoder()
    # decoder = get_decoder(autoencoder, encoding_dim)
    self.decoder = None

  def get_encoder(self):
    # this model maps an input to its encoded representation
    encoder = Model(self.autoencoder.input, self.autoencoder.layers[6].output)

    return encoder

  def get_decoder(self, autoencoder, encoding_dim):
    decoder_input = Input(shape=(encoding_dim,))
    decoder = Model(decoder_input, autoencoder.layers[-1](decoder_input))

    return decoder

  def train(self, x_train, x_test):
    self.autoencoder.fit(x_train, x_train,
                         epochs=10,
                         batch_size=128,
                         shuffle=True,
                         validation_data=(x_test, x_test),
                         callbacks=[TensorBoard(log_dir='/tmp/autoencoder')])

    self.autoencoder.save('my_model.h5')

  def test(self, x_test):
    # encode and decode some digits
    # note that we take them from the *test* set
    # encoded_imgs = encoder.predict(x_test)
    # decoded_imgs = decoder.predict(encoded_imgs)

    import matplotlib.pyplot as plt

    decoded_imgs = self.autoencoder.predict(x_test)

    n = 10
    plt.figure(figsize=(20, 4))
    for i in range(1, n):
      # display original
      ax = plt.subplot(2, n, i)
      plt.imshow(x_test[i].reshape(28, 28))
      plt.gray()

      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)

      # display reconstruction
      ax = plt.subplot(2, n, i + n)
      plt.imshow(decoded_imgs[i].reshape(28, 28))
      plt.gray()

      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)

    plt.show()

    encoded_imgs = self.encoder.predict(x_test)

    n = 10
    plt.figure(figsize=(20, 8))
    for i in range(1, n):
      ax = plt.subplot(1, n, i)

      plt.imshow(encoded_imgs[i].reshape(4, 4 * 8).T)
      plt.gray()

      ax.get_xaxis().set_visible(False)
      ax.get_yaxis().set_visible(False)

    plt.show()

  def compare(self, img1, img2):
    encoded1 = self.encoder.predict(np.array([img1, ]))
    encoded2 = self.encoder.predict(np.array([img2, ]))

    size = encoded1.size

    sub = np.absolute(encoded1 - encoded2)
    similarity = 1 - np.sum(sub) / size

    return similarity


def load_data():
  from keras.datasets import mnist
  (x_train, y_train), (x_test, y_test) = mnist.load_data()

  x_train = x_train.astype('float32') / 255.
  x_test = x_test.astype('float32') / 255.
  x_train = np.reshape(x_train, (len(x_train), 28, 28, 1))  # adapt this if using `channels_first` image data format
  x_test = np.reshape(x_test, (len(x_test), 28, 28, 1))  # adapt t

  print(x_train.shape)
  print(x_test.shape)

  return (x_train, y_train), (x_test, y_test)


if __name__ == '__main__':
  (x_train, y_train), (x_test, y_test) = load_data()

  autoencoder = Autoencoder()
  # autoencoder.test(x_test)

  print(y_test)
  for i in range(len(x_test) - 1):
    sim = autoencoder.compare(x_test[0, :, :], x_test[i + 1, :, :])
    if y_test[i] == y_test[i + 1]:
      print(sim)

