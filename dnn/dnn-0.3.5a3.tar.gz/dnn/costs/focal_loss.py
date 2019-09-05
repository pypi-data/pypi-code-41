import tensorflow as tf
from tensorflow.python.ops import array_ops

def focal_loss (labels, logits, alpha = 0.25, gamma = 2):
    r"""Compute focal loss for predictions.
        Multi-labels Focal loss formula:
            FL = -alpha * (z-p)^gamma * log(p) -(1-alpha) * p^gamma * log(1-p)
                 ,which alpha = 0.25, gamma = 2, p = sigmoid(x), z = target_tensor.
    Args:
     logits: A float tensor of shape [batch_size, num_anchors,
        num_classes] representing the predicted logits for each class
     labels: A float tensor of shape [batch_size, num_anchors,
        num_classes] representing one-hot encoded classification targets     
     alpha: A scalar tensor for focal loss alpha hyper-parameter
     gamma: A scalar tensor for focal loss gamma hyper-parameter
    Returns:
        loss: A (scalar) tensor representing the value of the loss function
    """
    p = tf.nn.sigmoid (logits)
    zeros = array_ops.zeros_like (p, dtype = p.dtype)
    # For poitive prediction, only need consider front part loss, back part is 0;
    # target_tensor > zeros <=> z=1, so poitive coefficient = z - p.
    pos_p_sub = array_ops.where (labels > zeros, labels - p, zeros)    
    # For negative prediction, only need consider back part loss, front part is 0;
    # target_tensor > zeros <=> z=1, so negative coefficient = 0.
    neg_p_sub = array_ops.where (labels > zeros, zeros, p)
    per_entry_cross_ent = - alpha * (pos_p_sub ** gamma) * tf.log (tf.clip_by_value (p, 1e-8, 1.0)) \
                          - (1 - alpha) * (neg_p_sub ** gamma) * tf.log (tf.clip_by_value(1.0 - p, 1e-8, 1.0))
    return tf.reduce_sum (per_entry_cross_ent, axis = 1)

def categorical_focal_loss (labels, logits, alpha = 0.25, gamma = 2):
  """
  :param y_true: A tensor of the same shape as `y_pred`
  :param y_pred: A tensor resulting from a softmax
  :return: Output tensor.
  """

  # Scale predictions so that the class probas of each sample sum to 1
  logits /= tf.reduce_sum (logits, axis=-1, keepdims=True)

  # Clip the prediction value to prevent NaN's and Inf's
  epsilon = 1e-8
  y_pred = tf.clip_by_value (y_pred, epsilon, 1. - epsilon)

  # Calculate Cross Entropy
  cross_entropy = -labels * tf.log (logits)

  # Calculate Focal Loss
  loss = alpha * tf.pow (1 - logits, gamma) * cross_entropy

  # Sum the losses in mini_batch
  return tf.reduce_sum(loss, axis = 1)    

def binary_focal_loss (labels, logits, alpha = 0.25, gamma = 2):
  """
  :param y_true: A tensor of the same shape as `y_pred`
  :param y_pred:  A tensor resulting from a sigmoid
  :return: Output tensor.
  """
  pt_1 = tf.where(tf.equal(labels, 1), y_pred, tf.ones_like(logits))
  pt_0 = tf.where(tf.equal(labels, 0), y_pred, tf.zeros_like(logits))

  epsilon = 1e-8
  # clip to prevent NaN's and Inf's
  pt_1 = tf.clip_by_value (pt_1, epsilon, 1. - epsilon)
  pt_0 = tf.clip_by_value (pt_0, epsilon, 1. - epsilon)

  return -tf.reduce_sum (alpha * K.pow(1. - pt_1, gamma) * tf.log(pt_1)) \
          -tf.reduce_sum ((1 - alpha) * tf.pow(pt_0, gamma) * tf.log(1. - pt_0))
          

'''
def sigmoid_focal_loss (labels, logits, alpha = 0.25, gamma = 2):
    """
    Computer focal loss for binary classification
    Args:
      labels: A int32 tensor of shape [batch_size].
      logits: A float32 tensor of shape [batch_size].
      alpha: A scalar for focal loss alpha hyper-parameter. If positive samples number
      > negtive samples number, alpha < 0.5 and vice versa.
      gamma: A scalar for focal loss gamma hyper-parameter.
    Returns:
      A tensor of the same shape as `lables`
    """
    y_pred = tf.nn.sigmoid (logits)
    labels = tf.to_float (labels)
    L = -labels * (1 - alpha) * ((1 - y_pred) * gamma) * tf.log (y_pred) - \
      (1 - labels) * alpha * (y_pred ** gamma) * tf.log (1 - y_pred)
    return L

def softmax_focal_loss (labels, logits, gamma = 2):
    """
    Computer focal loss for multi classification
    Args:
      labels: A int32 tensor of shape [batch_size].
      logits: A float32 tensor of shape [batch_size,num_classes].
      gamma: A scalar for focal loss gamma hyper-parameter.
    Returns:
      A tensor of the same shape as `lables`
    """
    y_pred = tf.nn.softmax (logits, axis = 1) # [batch_size,num_classes]
    # labels = tf.one_hot (labels, depth = y_pred.shape [1])
    L = -labels * ((1.0 - y_pred) ** gamma) * tf.log (y_pred)
    L = tf.reduce_sum (L, axis = 1)
    return L
'''