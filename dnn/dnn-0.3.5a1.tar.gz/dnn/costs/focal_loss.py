import tensorflow as tf
from tensorflow.python.ops import array_ops


def sigmoid_focal_loss (labels, logits, alpha = 0.25, gamma = 2):
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

def softmax_focal_loss (labels, logits, alpha = 0.25, gamma = 2):
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
    per_row_cross_ent = tf.nn.softmax_cross_entropy_with_logits (labels = labels, logits = logits)    
    p = tf.nn.softmax (logits)
    p_t = ((labels * p) +
           ((1 - labels) * (1 - p)))
    modulating_factor = tf.pow (1.0 - p_t, gamma)
    alpha_weight_factor = (labels * alpha + (1 - labels) * (1 - alpha))
    per_entry_cross_ent = modulating_factor * alpha_weight_factor * per_row_cross_ent
    return tf.reduce_sum (per_entry_cross_ent, axis = 1)


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