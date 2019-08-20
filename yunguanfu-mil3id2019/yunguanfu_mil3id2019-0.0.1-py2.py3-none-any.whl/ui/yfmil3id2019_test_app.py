# coding=utf-8

""" Put a useful module description here. Import whatever you want. """
import six


def run_app(network, weights, image, output, verbose):

    """ Run the application, using command line args. """
    six.print_("Network argument=" + str(network))
    six.print_("Weights argument=" + str(weights))
    six.print_("Image argument=" + str(image))
    six.print_("Output argument=" + str(output))
    six.print_("Verbose argument=" + str(verbose))
