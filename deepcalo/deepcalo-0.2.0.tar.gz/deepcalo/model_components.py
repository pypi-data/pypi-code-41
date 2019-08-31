import numpy as np
import copy
import functools
import keras as ks
import keras.backend as K

from keras_contrib.optimizers import Padam, Yogi
from keras_contrib.layers import GroupNormalization
# Uncomment the following (and in get_optimizer) if you have backend set to Tensforflow and want to use on the listed optimizers
# from tensorflow.contrib.opt import AdamWOptimizer, PowerSignOptimizer, AddSignOptimizer, ShampooOptimizer

# Internal imports
from .utils import merge_dicts, get_str_combs
from .layers import FiLM, ParametricGauss, SwitchNormalization


def get_loss_function(loss, is_tensor=True):
    '''
    Returns a loss function.

    Works both for Keras tensors as well as numpy ndarrays, see is_tensor
    argument.

    Args:
    -----
        loss : *str*
            Name of loss function. Supported loss function names are:
                Keras in-built functions
                Custom functions:
                    'mse_sqrtnorm', 'msesqrt_sqrtnorm', 'mae_sqrtnorm',
                    'maesqrt_sqrtnorm', 'logcosh_sqrtnorm',
                    'logcoshsqrt_sqrtnorm', 'Z_abs', 'Z_sq'
                Keras in-built metrics (do not use as loss function)

        is_tensor : *bool*
            If True, get_loss_function returns a function that works with
            Keras tensors (of type keras.backeend.variable).
            If false, the returned function works with numpy ndarrays (of type
            numpy.ndarray).

            Technical note regarding speed: This is done through the decorator
            convert_if_not_tensor, which first converts inputs to the loss
            function to Keras tensors, call the function as if is_tensor was
            True, then converts the result back to a numpy.ndarray. This
            conversion in the case of the inputs being ndarrays adds some
            overhead, and is only intended to be used in an evaluation setting,
            as opposed to a training setting.

    Returns:
    --------
        *function*
    '''

    def convert_if_not_tensor(is_tensor):
        '''Decorator function for handling different datatypes.'''

        def actual_decorator(loss_function):
            @functools.wraps(loss_function)
            def wrapper(y_true, y_pred):
                if is_tensor:
                    return loss_function(y_true, y_pred)
                else:
                    y_true_as_tensor = K.variable(y_true)
                    y_pred_as_tensor = K.variable(y_pred)
                    return K.eval(loss_function(y_true_as_tensor, y_pred_as_tensor))
            return wrapper

        return actual_decorator

    try:
        return convert_if_not_tensor(is_tensor)(ks.losses.get(loss))
    except:
        pass

    try:
        return convert_if_not_tensor(is_tensor)(ks.metrics.get(loss))
    except:
        pass

    # Example of custom loss function/metric
    if loss.lower() in ['zsq', 'z_sq']:
        @convert_if_not_tensor(is_tensor)
        def Z_sq(y_true, y_pred):
            return K.mean(K.pow(y_pred - y_true / y_true, 2), axis=-1)
        return Z_sq


def get_optimizer(optimizer):
    '''
    Returns :
        *Keras Optimizer instance*
    '''

    try:
        return ks.optimizers.get(optimizer)
    except:
        pass

    if isinstance(optimizer, dict):
        optimizer, kwargs = optimizer['class_name'], optimizer['config']
    else:
        kwargs = {}

    if optimizer.lower() in ['padam']: # Defaults: lr=0.1, beta_1=0.9, beta_2=0.999, epsilon=1e-8, decay=0., amsgrad=False, partial=1. / 8.
        return Padam(**kwargs)

    elif optimizer.lower() in ['yogi']: # Defaults: lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=1e-3, decay=0.
        return Yogi(**kwargs)

    # elif optimizer.lower() in ['adamw', 'adam_w']: # Defaults: As Adam
    #     tfoptimizer = AdamWOptimizer(**kwargs)
    #     return ks.optimizers.TFOptimizer(tfoptimizer)
    #
    # elif optimizer.lower() in ['powersign', 'power_sign']: # Defaults: learning_rate=0.1, base=math.e, beta=0.9, sign_decay_fn=None
    #     tfoptimizer = PowerSignOptimizer(**kwargs)
    #     return ks.optimizers.TFOptimizer(tfoptimizer)
    #
    # elif optimizer.lower() in ['addsign', 'add_sign']: # Defaults: learning_rate=0.1, alpha=1.0, beta=0.9
    #     tfoptimizer = AddSignOptimizer(**kwargs)
    #     return ks.optimizers.TFOptimizer(tfoptimizer)
    #
    # elif optimizer.lower() in ['shampoo']: # Defaults: global_step=0, max_matrix_size=768, gbar_decay=0.0, gbar_weight=1.0, mat_gbar_decay=1.0,
    #                                        # mat_gbar_weight=1.0, learning_rate=1.0, svd_interval=1 (20), precond_update_interval=1 (10),
    #                                        # epsilon=0.0001, alpha=0.5, use_iterative_root=False
    #     tfoptimizer = ShampooOptimizer(**kwargs)
    #     return ks.optimizers.TFOptimizer(tfoptimizer)

    else:
        raise NameError(f'Optimizer name {optimizer} not recognized.')


def get_activation(activation='linear'):
    '''
    Adds an activation layer to a graph.

    Args:
    -----
        activation : *str or config dict*
            The name of an activation function.
            One of 'relu', 'leakyrelu', 'prelu', 'elu', 'mrelu', 'swish',
            'gauss', 'gauss_f', 'pgauss', 'pgauss_f' (or any of their
            aliases), or anything that Keras will recognize as an
            activation function name.

    Returns:
    --------
        *Keras layer instance*
    '''
    if activation is None:
        activation = 'linear'

    if isinstance(activation, dict):
        activation, kwargs = activation['class_name'], activation['config']
    else:
        kwargs = {}

    if activation.lower() in ['relu']:
        act = ks.layers.ReLU(**kwargs)

    elif activation.lower() in ['leakyrelu', 'leaky_relu']:
        act = ks.layers.LeakyReLU(**kwargs)

    elif activation.lower() in ['prelu', 'p_relu']:
        act = ks.layers.PReLU(**kwargs)

    elif activation.lower() in ['elu']:
        act = ks.layers.ELU(**kwargs)

    elif activation.lower() in ['swish']:
        def swish(x):
            return K.sigmoid(x) * x
        act = ks.layers.Activation(swish, **kwargs)

    elif activation.lower() in ['mrelu', 'm_relu']:
        def mrelu(x):
            return K.minimum(K.maximum(1-x, 0), K.maximum(1+x, 0))
        act = ks.layers.Activation(mrelu, **kwargs)

    elif activation.lower() in ['gauss', 'gaussian']:
        def gauss(x):
            return K.exp(-x**2)
        act = ks.layers.Activation(gauss, **kwargs)

    elif activation.lower() in get_str_combs(['gauss','gaussian'], ['f','flipped']):
        def gauss_f(x):
            return 1 - K.exp(-x**2)
        act = ks.layers.Activation(gauss_f, **kwargs)

    elif activation.lower() in get_str_combs(['gauss','gaussian'], ['p','parametric']):
        act = ParametricGauss(flipped=False, **kwargs)

    elif activation.lower() in get_str_combs(get_str_combs(['gauss','gaussian'], ['p','parametric']), ['f', 'flipped']):
        act = ParametricGauss(flipped=True, **kwargs)

    else:
        act = ks.layers.Activation(activation, **kwargs)

    return act


def get_downsampling(tns, downsampling):
    '''
    Adds downsampling layer to a graph.

    Note that no kernel_initializer or regularization arguments are currently
    passed to the conv layer (when downsampling=='strided').

    Args:
    -----
        tns : *Keras tensor*
            Input tensor.

        downsampling : *str or config dict*
            The wanted way of downsampling.
            One of 'avgpool', 'maxpool' or 'strided'.

    Returns:
    --------
        *Keras tensor*
    '''

    if downsampling is None:
        return tns

    if isinstance(downsampling, dict):
        downsampling, kwargs = downsampling['class_name'], downsampling['config']
    else:
        kwargs = {}

    input_shape = tns._keras_shape

    if len(input_shape) == 4: # 2D convolution

        if downsampling == 'avgpool':
            return ks.layers.AveragePooling2D(**kwargs)(tns)
        elif downsampling == 'maxpool':
            return ks.layers.MaxPooling2D(**kwargs)(tns)
        elif downsampling == 'strided':
            n_channels = input_shape[-1] # Don't change the number of channels
            if 'kernel_size' not in kwargs:
                kwargs['kernel_size'] = 2
            if 'strides' not in kwargs:
                kwargs['strides'] = 2
            return ks.layers.Conv2D(filters=n_channels, **kwargs)(tns)

    elif len(input_shape) == 5: # 3D convolution

        if downsampling == 'avgpool':
            return ks.layers.AveragePooling3D(**kwargs)(tns)
        elif downsampling == 'maxpool':
            return ks.layers.MaxPooling3D(**kwargs)(tns)
        elif downsampling == 'strided':
            n_channels = input_shape[-1] # Don't change the number of channels
            if 'kernel_size' not in kwargs:
                kwargs['kernel_size'] = 2
            if 'strides' not in kwargs:
                kwargs['strides'] = 2
            return ks.layers.Conv3D(filters=n_channels, **kwargs)(tns)

    else:
        print('WARNING: Input not suitable for neither 2D nor 3D downsampling. Continuing without downsampling.')
        return tns


def get_normalization(tns=None, normalization='batch', freeze=False):
    '''
    Adds a normalization layer to a graph.

    Args:
    -----
        tns : *Keras tensor or None*
            Input tensor. If not None, then the graph will be connected through
            it, and a tensor will be returned. If None, the normalization layer
            will be returned.

        normalization : *str or config dict*

            The name of an normalization function.
            One of 'batch', 'layer', 'instance', or 'group' (or their aliases).
        freeze : *bool*
            Whether the beta and gamma parameters of normalization layer should
            be frozen or not.

    Returns:
    --------
        *Keras tensor or layer instance* (see tns argument)
    '''
    if isinstance(normalization, dict):
        normalization, config = normalization['class_name'], normalization['config']
    else:
        config = {}

    if freeze:
        freeze_kwargs = {'center':False, 'scale':False}
    else:
        freeze_kwargs = {}

    # Merge kwarg dicts
    kwargs = merge_dicts(config, freeze_kwargs)

    if normalization.lower() in get_str_combs(['batch'], ['norm','normalization','']):
        norm = ks.layers.BatchNormalization(**kwargs)

    elif normalization.lower() in get_str_combs(['layer'], ['norm','normalization','']):
        norm = GroupNormalization(groups=1, **kwargs)

    elif normalization.lower() in get_str_combs(['instance'], ['norm','normalization','']):
        if tns is None:
            raise Exception('Instance normalization needs a tns to be passed to '
                            'get_normalization.')
        n_features = tns._keras_shape[-1]
        norm = GroupNormalization(groups=n_features, **kwargs)

    elif normalization.lower() in get_str_combs(['group'], ['norm','normalization','']):
        norm = GroupNormalization(**kwargs)

    elif normalization.lower() in get_str_combs(['switch'], ['norm','normalization','']):
        norm = SwitchNormalization(**kwargs)

    else:
        raise NameError(f'Normalization name {normalization} not recognized.')

    if tns is not None:
        return norm(tns)
    else:
        return norm


def deserialize_layer_reg(layer_reg):

    deserialized_layer_reg = copy.deepcopy(layer_reg)

    for reg_type in deserialized_layer_reg:
        if reg_type in ['kernel_regularizer', 'bias_regularizer', 'activity_regularizer']:
            deserialized_layer_reg[reg_type] = ks.regularizers.get(deserialized_layer_reg[reg_type])
        elif reg_type in ['kernel_constraint', 'bias_constraint']:
            deserialized_layer_reg[reg_type] = ks.constraints.get(deserialized_layer_reg[reg_type])

    return deserialized_layer_reg


def upsample_img(tns, normalize=False, size=(1,1), interpolation='nearest'):

    def apply_normalization(tns):
        return tns / np.prod(size)
    tns = ks.layers.UpSampling2D(size=size, interpolation=interpolation,
                                 data_format='channels_last')(tns)
    if normalize:
        tns = ks.layers.Lambda(apply_normalization)(tns)

    return tns


def flatten_tns(tns):
    tns_shape = tns._keras_shape

    if len(tns_shape) > 2:
        # Dynamic flatten
        if all(dim is None for dim in tns_shape[1:3]):
            return ks.layers.Lambda(lambda x: K.batch_flatten(x))(tns)
        # Normal flatten
        else:
            return ks.layers.Flatten()(tns)
    else:
        return tns


def slice_tns(dimension, start=None, end=None, squeeze_axis=None):
    """
    Slices a tensor on a given dimension from start to end.
    Example : to slice tensor x[:, :, 5:10], call slice_tns(2, 5, 10) as you
    want to slice the second dimension.
    """
    def func(x):
        if dimension == 0:
            x = x[start:end]
        if dimension == 1:
            x = x[:, start:end]
        if dimension == 2:
            x = x[:, :, start:end]
        if dimension == 3:
            x = x[:, :, :, start:end]
        if dimension == 4:
            x = x[:, :, :, :, start:end]

        if squeeze_axis is not None:
            x = K.squeeze(x,squeeze_axis)

        return x

    return ks.layers.Lambda(func)


def get_norm_act(tns, activation=None, normalization=None, FiLM_tns=None):

    # Apply normalization
    if normalization is not None:
        tns = get_normalization(tns, normalization=normalization,
                                freeze=FiLM_tns is not None)

    # Condition using output of FiLM_gen
    if FiLM_tns is not None:
        tns = FiLM()([tns, FiLM_tns])

    return get_activation(activation)(tns)


def get_dense_norm_act(tns, units, initialization='orthogonal',
                       activation=None, normalization=None, layer_reg={},
                       dropout=None):

    for unit in units:
        tns = ks.layers.Dense(unit,
                              kernel_initializer=ks.initializers.get(initialization),
                              use_bias=False,
                              **deserialize_layer_reg(layer_reg))(tns)
        if dropout is not None:
            tns = ks.layers.Dropout(dropout)(tns)
        tns = get_norm_act(tns, activation, normalization)

    return tns


def squeeze_excite_module(input, ratio=16):
    ''' Create a channel-wise squeeze-excite block

    From https://github.com/titu1994/keras-squeeze-excite-network/blob/master/se.py

    Args:
        input: input tensor
        n_filters: number of output filters (feature maps)
    Returns: a keras tensor
    References
    -   [Squeeze and Excitation Networks](https://arxiv.org/abs/1709.01507)
    '''

    tns = input
    n_filters = tns._keras_shape[-1]
    se_shape = (1, 1, n_filters)

    if n_filters // ratio < 1:
        raise AssertionError('Please make sure that the number '
                             'of incoming channels is not less '
                             'than the ratio in the squeeze_excite_module.')

    tns = ks.layers.GlobalAveragePooling2D()(tns)
    tns = ks.layers.Reshape(se_shape)(tns)
    tns = ks.layers.Dense(n_filters // ratio, activation='relu',
                          kernel_initializer=initialization,
                          use_bias=False)(tns)
    tns = ks.layers.Dense(n_filters, activation='sigmoid',
                          kernel_initializer=initialization,
                          use_bias=False)(tns)

    return ks.layers.multiply([input, tns])


def conv_module(tns, n_filters, kernel_size=3, conv_dim=2, cardinality=1,
                use_squeeze_and_excite=False, squeeze_and_excite_ratio=16,
                cnn_type='simple', downsampling=None, downsample=False,
                min_size_for_downsampling=2, FiLM_tns=None,
                initialization='orthogonal', activation=None,
                normalization=None, layer_reg={}, dropout=None):

    def conv_drop_norm_act(tns, kernel_size=3, cardinality=1, use_bias=True,
                           norm_first=False, FiLM_tns=None):
        """Convenience function to use for both simple and res type CNNs."""

        def _get_norm_act_dropblock(tns):

            tns = get_norm_act(tns, activation, normalization, FiLM_tns)

            # Dropblock
            if dropout is not None:
                if conv_dim == 3:
                    raise Exception('3D convolutions and DrobBlock layers are '
                                    'currently not compatible.')
                if not isinstance(dropout, dict):
                    raise TypeError('Please pass a dict of keyword arguments to '
                                    'the DropBlock layer in the CNN.')
                else:
                    tns = DropBlock2D(**dropout)(tns)

            return tns

        # Normalization first
        if norm_first:
            tns = _get_norm_act_dropblock(tns)

        # Convolution
        if conv_dim == 2:
            if cardinality==1:
                tns = ks.layers.Conv2D(n_filters, kernel_size, use_bias=use_bias, padding='same',
                                       kernel_initializer=ks.initializers.get(initialization),
                                       **deserialize_layer_reg(layer_reg))(tns)
            elif cardinality > 1:
                n_filters_in_per_split = int(tns._keras_shape[-1] / cardinality)
                if n_filters_in_per_split < 1:
                    raise AssertionError('Please make sure that the number '
                                         'of incoming channels is not less '
                                         'than the cardinality.')
                n_filters_out_per_split = int(n_filters / cardinality)

                tns_pre_conv = tns
                group_list = []
                for c in range(cardinality):
                    tns = ks.layers.Lambda(lambda z: z[:, :, :, c * n_filters_in_per_split:(c + 1) * n_filters_in_per_split])(tns_pre_conv)
                    tns = ks.layers.Conv2D(n_filters_out_per_split, kernel_size, use_bias=use_bias, padding='same',
                                           kernel_initializer=ks.initializers.get(initialization),
                                           **deserialize_layer_reg(layer_reg))(tns)
                    group_list.append(tns)
                tns = ks.layers.concatenate(group_list)
            else:
                raise Exception('Please make sure that cardinality > 0.')

        elif conv_dim == 3:
            if not type(kernel_size)==tuple:
                kernel_size = (kernel_size,)*2 + (2,)
            if cardinality != 1:
                print('WARNING: 3D convolutions and grouped convolutions are '
                      'currently not compatible: cardinality != 1 is ignored.')
            tns = ks.layers.Conv3D(n_filters, kernel_size, use_bias=use_bias, padding='same',
                                   kernel_initializer=ks.initializers.get(initialization),
                                   **deserialize_layer_reg(layer_reg))(tns)

        # Normalization last
        if not norm_first:
            tns = _get_norm_act_dropblock(tns)

        return tns

    # Downsample
    if downsample and downsampling is not None:
        # Check if H,W are dynamic - if yes, do downsampling and hope for the best
        if all(dim is None for dim in tns._keras_shape[1:3]):
            tns = get_downsampling(tns, downsampling)
        else:
            # Check that both height and width are at least min_size_for_downsampling
            if all(dim >= min_size_for_downsampling for dim in tns._keras_shape[1:3]):
                tns = get_downsampling(tns, downsampling)

    if cnn_type == 'simple':
        tns = conv_drop_norm_act(tns, kernel_size=kernel_size,
                                 cardinality=cardinality, use_bias=True,
                                 norm_first=False, FiLM_tns=FiLM_tns)

        if use_squeeze_and_excite:
            tns = squeeze_excite_module(tns, squeeze_and_excite_ratio)

    elif cnn_type == 'res':
        # Project shortcut so it has compatible number of output feature maps
        if downsample:
            if conv_dim == 2:
                shortcut = ks.layers.Conv2D(n_filters, (1,1), padding='same',
                                       kernel_initializer=ks.initializers.get(initialization),
                                       **deserialize_layer_reg(layer_reg))(tns)
            elif conv_dim == 3:
                shortcut = ks.layers.Conv3D(n_filters, (1,1,1), padding='same',
                                       kernel_initializer=ks.initializers.get(initialization),
                                       **deserialize_layer_reg(layer_reg))(tns)
        else:
            shortcut = tns

        # First conv
        tns = conv_drop_norm_act(tns, kernel_size=kernel_size,
                                 cardinality=cardinality,
                                 use_bias=normalization is None,
                                 norm_first=True, FiLM_tns=None)

        # Second conv
        tns = conv_drop_norm_act(tns, kernel_size=kernel_size,
                                 cardinality=cardinality, use_bias=True,
                                 norm_first=True, FiLM_tns=FiLM_tns)

        if use_squeeze_and_excite:
            tns = squeeze_excite_module(tns, squeeze_and_excite_ratio)

        # Add
        tns = ks.layers.Add()([tns, shortcut])

    return tns
