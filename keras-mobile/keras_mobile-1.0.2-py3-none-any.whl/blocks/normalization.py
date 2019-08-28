from keras.layers import GlobalAveragePooling2D, Dense, Reshape
import keras.backend as K
from ..layers.normalization import AdaptiveInstanceLayerNormalization

def AdaptiveInstanceNormalization(light=False):
  """
    Port of UGATIT MLP+AdaptiveInstanceLayer
    Does not include the 2 fully connected layers from the original model (see https://github.com/taki0112/UGATIT/blob/bbb702eae945592853d1405e24d197b97a5a2c73/UGATIT.py#L170)
  """
  def stub(x):
    if light:
      x = GlobalAveragePooling2D()(x)
    
    x_shape = K.shape(x)

    gamma = Dense(x, x_shape[-1])
    gamma = Reshape((1, 1, x_shape[-1],))(gamma)
    
    beta  = Dense(x, x_shape[-1])
    beta  = Reshape((1, 1, x_shape[-1],))(gamma)

    x = AdaptiveInstanceLayerNormalization(gamma, beta)(x)
    
    return x

  return stub