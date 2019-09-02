# -*- coding: utf-8 -*-
import warnings
import numpy as np
from ..settings import AlgorithmTypes
from ..exceptions import MissingLinkException
from ..interfaces import GradCAMInterface, VisualBackPropInterface, ImageDimOrdering


class KerasVis(GradCAMInterface, VisualBackPropInterface):
    @classmethod
    def _get_input_dim(cls, model):
        from ..vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        if channels_first:
            # it means we have NCHW ordering
            _, depth, height, width = model.input_shape
        else:
            # we have NHWC ordering
            _, height, width, depth = model.input_shape

        return depth, height, width

    def _get_feature_maps(self, model, image, shape=None):
        from ..vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        # noinspection PyPep8Naming
        Convolution2D = dynamic_import.bring('layers.Convolution2D')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        input_, depth, height, width = self._get_scaled_input(image, shape)
        if channels_first:
            input_ = input_.transpose(2, 0, 1)

        layer_indexes = [ind for ind, el in enumerate(model.layers) if isinstance(el, Convolution2D)]
        layers = [model.layers[li].output for li in layer_indexes]
        get_feature = keras_backend.function([model.layers[0].input], layers)
        output = model.predict(np.expand_dims(input_, axis=0))
        feature_maps = get_feature([[input_]])
        return feature_maps, output

    @classmethod
    def _get_activation_and_grad_for_last_conv(cls, model, scores, input_=None):
        from ..vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        # noinspection PyPep8Naming
        Convolution2D = dynamic_import.bring('layers.Convolution2D')
        # noinspection PyPep8Naming
        Lambda = dynamic_import.bring('layers.core.Lambda')
        # noinspection PyPep8Naming
        Sequential = dynamic_import.bring('models.Sequential')
        # noinspection PyPep8Naming
        K = dynamic_import.bring('backend')

        def normalize(x):
            # utility function to normalize a tensor by its L2 norm
            return x / (K.sqrt(K.mean(K.square(x))) + 1e-5)

        def target_category_loss(x, category_index, nb_classes):
            return K.batch_dot(x, K.one_hot([category_index], nb_classes), axes=(1, 1))

        def target_category_loss_output_shape(input_shape):
            return input_shape

        def target_layer(x):
            return target_category_loss(x, pred_class, scores.shape[0])

        pred_class = np.argmax(scores)
        result_model = Sequential()
        result_model.add(model)
        result_model.add(Lambda(target_layer, output_shape=target_category_loss_output_shape))
        conv_layer_indexes = [i for i, layer in enumerate(model.layers) if isinstance(layer, Convolution2D)]
        if not conv_layer_indexes:
            raise MissingLinkException("Unable to find convolutional layer in the model!")

        conv_output = model.layers[conv_layer_indexes[-1]].output
        loss = K.sum(result_model.layers[-1].output)
        grads = normalize(K.gradients(loss, conv_output)[0])
        gradient_function = K.function([result_model.layers[0].input], [conv_output, grads])
        output, grads_val = gradient_function([np.expand_dims(input_, axis=0)])

        dim_ordering = K.image_dim_ordering()
        channels_first = dim_ordering == 'th'
        axis = (1, 2) if channels_first else (0, 1)
        a_weights = np.mean(grads_val[0], axis=axis)

        return output, a_weights

    def process_image(self, path=None, model=None, upload_images=None, seed_image=None):
        from ..vis.dynamic_import import DynamicImport

        warnings.warn("This method is deprecated. use 'generate_grad_cam' instead", DeprecationWarning)
        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        dim_order = ImageDimOrdering.NCHW if channels_first else ImageDimOrdering.NHWC

        self.generate_grad_cam(path, model, input_array=seed_image, dim_order=dim_order)

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NHWC, expected_class=None, keep_origin=False, description=None):
        try:
            images_data, top = self._generate_grad_cam(
                model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
                class_mapping=class_mapping, dim_order=dim_order)

        except MissingLinkException:
            self.logger.exception("Was not able to produce GradCAM images because of internal error!")
        else:
            images = self._prepare_images_payload(images_data, keep_origin, uri)
            meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.GRAD_CAM, uri)
            extra = {
                "expected_class": expected_class,
                "top": top,
            }
            meta.update(extra)
            model_hash = self._get_weights_hash(model)
            self.upload_images(model_hash, images, meta, description=description)

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NHWC,
                         expected_output=None, keep_origin=False, description=None):
        try:
            result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order)
        except MissingLinkException:
            self.logger.exception("Was not able to generate image with VisualBackProp because of internal error!")
        else:
            images = self._prepare_images_payload(result, keep_origin, uri)
            meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
            extra = {
                "expected_output": expected_output
            }
            meta.update(extra)
            model_hash = self._get_weights_hash(model)
            self.upload_images(model_hash, images, meta, description=description)

    def _get_prediction(self, model, image, shape=None):
        from ..vis.dynamic_import import DynamicImport

        dynamic_import = DynamicImport(model)
        keras_backend = dynamic_import.bring('backend')
        dim_ordering = keras_backend.image_dim_ordering()
        channels_first = dim_ordering == 'th'

        input_, depth, height, width = self._get_scaled_input(image, shape)
        if channels_first:
            input_ = input_.transpose(2, 0, 1)
        probs = model.predict(np.array([input_]))
        probs = np.squeeze(probs)
        return input_, probs

    def generate_guided_grad_cam(self):
        raise NotImplemented()
