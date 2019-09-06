# -*- coding: utf-8 -*-
import tflex
import argparse
import subprocess


def get_parser():
    parser = argparse.ArgumentParser(
        description='Convert source model(.pb,.h5,SavedModel) to target model(.tflex graph) supported on EPU.')
    parser.add_argument(
        '--keras_model', '-k',
        type=str,
        default='',
        help="Source model with .h5 file to be converted.")
    parser.add_argument(
        '--frozen_model', '-f',
        type=str,
        default='',
        help="Source model with .pb file to be converted.")
    parser.add_argument(
        '--saved_model', '-s',
        type=str,
        default='',
        help="Source SavedModel with .pb file and variables to be converted.")
    parser.add_argument(
        '--save_path', '-p',
        type=str,
        default='',
        help="Pathname to save the optimized graph(e.g., ./model.tflex).")
    parser.add_argument(
        '--input_arrays', '-i',
        type=str,
        default='input',
        help="String of input node names. If your model has more inputs, please use tflexconverter -i input_1,input_2.")
    parser.add_argument(
        '--output_arrays', '-o',
        type=str,
        default='output',
        help="String of output node names. If your model has more outputs, please use tflexconverter -o output_1,output_2.")
    parser.add_argument(
        '--device', '-d',
        type=str,
        default='/device:EPU:0',
        help="EPU devices assigned to the Conv2D, MaxPool and Pad ops, default is /device:EPU:0.")
    parser.add_argument(
        '--level', '-l',
        type=int,
        default=0,
        help="Fundamental, BatchNormalization, EPU Core and Additional optimizations are available, default level=0 means that all optimizations will be executed")
    parser.add_argument(
        '--strict_padding', '-r',
        dest='strict_padding',
        action='store_true',
        help="EPU MaxPool only support padding is SAME or VALID(without remnant in W/H). If True is set, it will execute on the CPU.")

    return parser


def main():
    parser = get_parser()
    flags = parser.parse_args()
    if flags.frozen_model:
        input_arrays = []
        output_arrays = []
        if flags.input_arrays and flags.output_arrays:
            for name in flags.input_arrays.split(','):
                input_arrays.append(name)
            for name in flags.output_arrays.split(','):
                output_arrays.append(name)
            converter = tflex.Converter.from_frozen_graph(flags.frozen_model, input_arrays, output_arrays)
            converter.convert(flags.save_path, flags.device, flags.level, flags.strict_padding)
        else:
            raise ValueError('--input_arrays and --output_arrays are required.')

    elif flags.keras_model:
        converter = tflex.Converter.from_keras_model(flags.keras_model)
        converter.convert(flags.save_path, flags.device, flags.level, flags.strict_padding)
    elif flags.saved_model:
        converter = tflex.Converter.from_saved_model(flags.saved_model)
        converter.convert(flags.save_path, flags.device, flags.level, flags.strict_padding)
    else:
        subprocess.call(['tflexconverter -h'], shell=True)


if __name__ == '__main__':
    main()
