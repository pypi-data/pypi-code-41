import numpy as np
import abc
import six

from ..settings import AlgorithmTypes
from ..interfaces import GradCAMInterface, ImageDimOrdering, VisualBackPropInterface
from ..exceptions import MissingLinkException


@six.add_metaclass(abc.ABCMeta)
class TensorFlowVis(GradCAMInterface, VisualBackPropInterface):
    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NHWC, expected_class=None, keep_origin=False, description=None):
        try:
            images_data, top = self._generate_grad_cam(
                model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
                class_mapping=class_mapping, dim_order=dim_order)
        except MissingLinkException:
            self._logger.exception("Was not able to produce GradCAM images because of internal error!")
        else:
            # noinspection PyProtectedMember
            images = self._project._prepare_images_payload(images_data, keep_origin, uri)
            # noinspection PyProtectedMember
            meta = self._project._get_toplevel_metadata(self._project._test_token, AlgorithmTypes.GRAD_CAM, uri)
            extra = {
                "expected_class": expected_class,
                "top": top,
            }
            meta.update(extra)
            model_hash = self.get_weights_hash(model)
            self._project.upload_images(model_hash, images, meta, description=description)

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NHWC,
                         expected_output=None, keep_origin=False, description=None):
        try:
            result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order)
        except MissingLinkException:
            self._logger.exception("Was not able to generate image with VisualBackProp because of internal error!")
        else:
            # noinspection PyProtectedMember
            images = self._project._prepare_images_payload(result, keep_origin, uri)
            # noinspection PyProtectedMember
            meta = self._project._get_toplevel_metadata(self._project._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
            extra = {
                "expected_output": expected_output
            }
            meta.update(extra)
            model_hash = self._project._get_weights_hash(model)
            self._project.upload_images(model_hash, images, meta, description=description)

    def _get_activation_and_grad_for_last_conv(self, model, scores, input_=None):
        import tensorflow as tf

        last_conv_layer_name = self._tf_properties.get("last_conv_layer")
        if last_conv_layer_name:
            last_conv = self._get_tensor_from_name(model, last_conv_layer_name, "name")
        else:
            last_conv = self._get_tensor_from_name(model, "conv2d", "type", expect_many=True)

        if last_conv is None:
            raise MissingLinkException("Cannot determine last convolutional layer. Try to provide name of last conv "
                                       "layer explicitly via set_tf_properties. "
                                       "e.g. experiment.set_tf_properties(last_conv_layer='conv5_3/conv2d')")
        output_layer = self._tf_properties["__output_layer"]
        input_placeholder = self._determine_input_placeholder(model)

        signal = tf.multiply(output_layer, scores)
        loss = tf.reduce_mean(signal)
        grads = tf.gradients(loss, last_conv)[0]
        normalize_grads = tf.div(grads, tf.sqrt(tf.reduce_mean(tf.square(grads))) + tf.constant(1e-5))
        output, grads_val = model.run([last_conv, normalize_grads], feed_dict={input_placeholder: np.array([input_])})

        grads_val = grads_val[0]
        a_weights = np.mean(grads_val, axis=(0, 1))
        return output, a_weights

    def _get_feature_maps(self, model, image, shape=None):
        input_, depth, height, width = self._get_scaled_input(image, shape)
        output_layer_name = self._tf_properties.get("output_layer")
        if output_layer_name is None:
            raise MissingLinkException("Please provide 'output_layer' via set_tf_properties.")
        output_layer = self._get_tensor_from_name(model, output_layer_name, "name")
        if output_layer is None:
            raise MissingLinkException("Was not able to find op named %s" % output_layer_name)

        all_conv = self._get_tensor_from_name(model, "conv2d", "type", expect_many=True, return_many=True,
                                              reverse_order=False)
        if len(all_conv) == 0:
            raise MissingLinkException("Was not able to determine Conv2D layers in the network. "
                                       "Make sure you have some.")
        input_placeholder = self._determine_input_placeholder(model)
        all_conv.append(output_layer)
        result = model.run(all_conv, feed_dict={input_placeholder: np.array([input_])})
        maps = result[:-1]
        output = result[-1]
        return maps, output

    def _get_tensor_from_name(self, model, name, by_attr, expect_many=False, return_many=False, reverse_order=True):
        name = str(name).lower()
        operations = model.graph.get_operations()
        if reverse_order:
            operations = operations[::-1]  # will start seeking from the end
        ops = [op for op in operations if str(getattr(op, by_attr)).lower() == name]
        if len(ops) > 1 and not expect_many:
            self._logger.warning("Unexpected length of ops %s retrieved by op.%s=%s", len(ops), by_attr, name)
        elif len(ops) == 0:
            self._logger.warning("No op found by op.%s=%s", by_attr, name)
            return None
        if return_many:
            tensors = [self.__get_tensor_from_op(i) for i in ops]
            return tensors
        single_op = ops[0]
        tensor = self.__get_tensor_from_op(single_op)

        return tensor

    def _determine_input_placeholder(self, model):
        input_placeholder = self._tf_properties.get("__input_placeholder")
        if input_placeholder is not None:
            return input_placeholder
        pl_name = self._tf_properties.get("input_placeholder")
        if pl_name is not None:
            pl = self._get_tensor_from_name(model, pl_name, "name", reverse_order=False)
        else:
            pl = self._get_tensor_from_name(model, "placeholder", "type", reverse_order=False)
        if pl is None:
            message = "Cannot infer placeholder for input data. " \
                      "Please use 'set_tf_properties' and specify 'input_placeholder'. " \
                      "e.g. experiment.set_tf_properties(input_placeholder=X)"
            self._logger.error(message)
            raise MissingLinkException(message)
        self._tf_properties["__input_placeholder"] = pl  # note: here we save a placeholder instance, not a name

        return pl

    def _get_input_dim(self, model):
        pl = self._determine_input_placeholder(model)
        try:
            shape = pl.shape.as_list()
        except ValueError as ex:
            self._logger.exception(ex)
            raise MissingLinkException("Was not able to determine input shape. Please set it via set_tf_properties!")
        shape = shape[1:]  # excluding batch size
        h, w, d = shape
        shape = (d, h, w)  # shape has to be in format: depth, height, width regardless of framework ordering

        return shape

    def _get_prediction(self, model, image, shape=None):
        input_, depth, height, width = self._get_scaled_input(image, shape)
        output_layer_name = self._tf_properties.get("output_layer")
        if output_layer_name is not None:
            output_layer = self._get_tensor_from_name(model, output_layer_name, "name")
        else:
            output_layer = self._get_tensor_from_name(model, "softmax", "type")
        if output_layer is None:
            raise MissingLinkException("Please provide output operation via set_tf_properties. "
                                       "e.g. experiment.set_tf_properties(output_layer='softmax')")
        self._tf_properties["__output_layer"] = output_layer
        input_placeholder = self._determine_input_placeholder(model)
        probs = model.run(output_layer, feed_dict={input_placeholder: np.array([input_])})
        probs = np.squeeze(probs)

        return input_, probs

    def __get_tensor_from_op(self, op):
        outputs = op.outputs
        if len(outputs) > 1:
            self._logger.warning("Length of outputs of 'op' is %s", len(outputs))
        elif len(outputs) == 0:
            raise MissingLinkException("Operation node has empty 'outputs'")

        return outputs[0]
