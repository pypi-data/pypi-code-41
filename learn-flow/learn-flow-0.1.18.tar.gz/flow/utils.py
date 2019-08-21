# -*- coding: utf-8 -*-
"""
module learner.py
--------------------
A base class definition for the learner class.
The default learner defines steps for the learning procedure.
"""
import tensorflow as tf
import numpy as np
from blinker import signal
import time


def initialize_session():
    """
    Runs the initializer for all not initialized variables in the default graph.
    """
    sess = tf.get_default_session()
    not_initialized = sess.run([tf.is_variable_initialized(var) for var in tf.global_variables()])
    not_initialized = [v for (v, f) in zip(tf.global_variables(), not_initialized) if not f]
    if len(not_initialized) > 0:
        sess.run(tf.variables_initializer(not_initialized))


def reinitialize_all_variables():
    """
    Runs the initializer for all variables in the default graph.
    """
    sess = tf.get_default_session()
    all_variables = [var for var in tf.global_variables()]
    if len(all_variables) > 0:
        sess.run(tf.variables_initializer(all_variables))


def partial_restore_op(save_path):
    """
    An op that restore the subset of variables defined on the default graph that is stored on the given checkpoint.
    :param save_path: a checkpoint path.
    :return: the restore op
    """
    from tensorflow.python import pywrap_tensorflow
    from tensorflow.python.tools import inspect_checkpoint as chkp
    # chkp.print_tensors_in_checkpoint_file()
    reader = pywrap_tensorflow.NewCheckpointReader(save_path)
    var_to_shape_map = reader.get_variable_to_shape_map()
    all_vars = tf.global_variables()
    allvars_dic = dict()

    for var in all_vars:
        allvars_dic[var.name[:-2]] = var
    var_list = list()
    for key in sorted(var_to_shape_map):
        t = reader.get_tensor(key)
        var_list.append(tf.assign(allvars_dic[key], t))
    return tf.group(var_list)


def count_params():
    """
    Counts the total number of trainable parameters.
    :return: the count of trainable parameters.
    """
    all_vars = tf.trainable_variables()
    total = 0
    for var in all_vars:
        p = np.prod(var.shape.as_list())
        total += p
    return total


def get_not_in_checkpoint_variables(save_path):
    """
    Inspect the given checkpoint and returns a list of variable names defined on default tensorflow graph
    that is not defined on the checkpoint.
    :param save_path: a checkpoint path.
    :return: list of not in checkpoint variable names.
    """
    from tensorflow.python import pywrap_tensorflow
    from tensorflow.python.tools import inspect_checkpoint as chkp
    # chkp.print_tensors_in_checkpoint_file()
    reader = pywrap_tensorflow.NewCheckpointReader(save_path)
    var_to_shape_map = reader.get_variable_to_shape_map()
    all_vars = tf.global_variables()
    allvars_dic = dict()

    for var in all_vars:
        allvars_dic[var.name[:-2]] = var
    var_list = list()

    for key in allvars_dic.keys():
        if key not in var_to_shape_map:
            var_list.append(key)
    # for key in sorted(var_to_shape_map):
    #     t = reader.get_tensor(key)
    #     var_list.append(tf.assign(allvars_dic[key], t))
    # return tf.group(var_list)
    print(">>>>>>ckpt_path>>>>>", save_path)
    print(">>>>>not_in_checkpoint", var_list)
    return var_list
