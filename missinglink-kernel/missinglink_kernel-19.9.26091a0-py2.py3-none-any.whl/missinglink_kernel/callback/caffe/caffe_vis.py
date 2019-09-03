import warnings
import numpy as np
from ..settings import AlgorithmTypes
from ..exceptions import MissingLinkException
from ..interfaces import GradCAMInterface, VisualBackPropInterface, ImageDimOrdering


class CaffeVis(GradCAMInterface, VisualBackPropInterface):
    def generate_guided_grad_cam(self):
        pass

    def process_image(self, path, net, scores=None, top_classes=5, top_images=1, class_mapping=None):
        warnings.warn("This method is deprecated. use 'generate_grad_cam' instead", DeprecationWarning)
        self.generate_grad_cam(
            path, net, input_array=None, top_classes=top_classes, top_images=top_images, class_mapping=class_mapping)

    def generate_grad_cam(self, uri=None, model=None, input_array=None, top_classes=5, top_images=1, class_mapping=None,
                          dim_order=ImageDimOrdering.NCHW, expected_class=None, keep_origin=False, description=None):

        images_data, top = self._generate_grad_cam(
            model, uri=uri, input_array=input_array, top_classes=top_classes, top_images=top_images,
            class_mapping=class_mapping, dim_order=dim_order)
        images = self._prepare_images_payload(images_data, keep_origin, uri)
        meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.GRAD_CAM, uri)
        extra = {
            "expected_class": expected_class,
            "top": top,
        }
        meta.update(extra)
        model_hash = self.calculate_weights_hash(model)
        self.upload_images(model_hash, images, meta, description=description)

    def visual_back_prop(self, uri=None, model=None, input_val=None, dim_order=ImageDimOrdering.NCHW,
                         expected_output=None, keep_origin=False, description=None):
        result = self._visual_back_prop(model, uri=uri, input_val=input_val, dim_order=dim_order)
        images = self._prepare_images_payload(result, keep_origin, uri)
        meta = self._get_toplevel_metadata(self._test_token, AlgorithmTypes.VISUAL_BACKPROP, uri)
        extra = {
            "expected_output": expected_output
        }
        meta.update(extra)
        model_hash = self.calculate_weights_hash(model)
        self.upload_images(model_hash, images, meta, description=description)

    @classmethod
    def _get_activation_and_grad_for_last_conv(cls, model, scores, input_=None):
        layer_names = list(model._layer_names)
        conv_layers = [index for index, i in enumerate(model.layers) if i.type == "Convolution"]
        if not conv_layers:
            raise MissingLinkException("It looks like you model does not have any convolutional layer. "
                                       "Cannot generate GradCAM.")
        last_conv = layer_names[conv_layers[-1]]    # take the last conv layer
        if len(scores.shape) == 1:  # means it is a 1d array and network expects 2d, so we just add 0 axis
            scores = np.expand_dims(scores, axis=0)
        try:
            diff = model.backward(end=last_conv, prob=scores)
        except Exception as ex:
            # noinspection PyUnresolvedReferences
            if 'diff is not 4-d' in ex.message:
                scores = cls.__old_caffe_backward_workaround(scores)
                diff = model.backward(end=last_conv, prob=scores)
            else:
                # noinspection PyUnresolvedReferences
                raise MissingLinkException(ex.message)
        activation_lastconv = model.blobs[last_conv].data
        grads = model.blobs[last_conv].diff[0]
        # axis here depend on ordering. here it is CHW which is why axis=(1,2) for H and W
        a_weights = np.mean(grads, axis=(1, 2))
        return activation_lastconv, a_weights

    def _get_feature_maps(self, model, image, shape=None):
        # noinspection PyUnresolvedReferences
        import caffe

        input_, depth, height, width = self._get_scaled_input(image, shape)
        transformer = caffe.io.Transformer({'data': model.blobs['data'].data.shape})
        if depth > 1:  # if image is not grayscale
            transformer.set_transpose('data', (2, 0, 1))
        model.blobs['data'].reshape(*np.asarray([1, depth, height, width]))  # run only one image
        model.blobs['data'].data[...][0, :, :, :] = transformer.preprocess('data', input_)
        out = model.forward()

        layer_names = list(model._layer_names)

        conv_layers_names = [layer_names[index] for index, i in enumerate(model.layers) if i.type == "Convolution"]
        if not conv_layers_names:
            message = "It looks like you model does not have any convolutional layer."
            self.logger.error(message)
            raise MissingLinkException(message)

        activations = [model.blobs[conv].data for conv in conv_layers_names]
        return activations, out

    def _get_prediction(self, net, image, shape=None):
        # noinspection PyUnresolvedReferences
        import caffe

        input_, depth, height, width = self._get_scaled_input(image, shape)
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        if depth > 1:  # if image is not grayscale
            transformer.set_transpose('data', (2, 0, 1))
        net.blobs['data'].reshape(*np.asarray([1, depth, height, width]))  # run only one image
        net.blobs['data'].data[...][0, :, :, :] = transformer.preprocess('data', input_)
        out = net.forward()
        scores = out['prob']
        scores = np.squeeze(scores)
        return input_, scores

    @classmethod
    def _get_input_dim(cls, model):
        _, depth, height, width = list(model.blobs["data"].data.shape)
        return depth, height, width
