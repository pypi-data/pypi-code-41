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
        '--path_name', '-p',
        type=str,
        default='',
        help="Directory to save the optimized graph(i.e.,model.tflex file will be saved here).")
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
        default=4,
        help="Fundamental, BatchNormalization, EPU Core and Additional optimizations are available, default level=4 means that all optimizations will be executed.")
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
            if flags.path_name:
                converter.convert(flags.path_name, flags.device, flags.level)
            else:
                model = flags.frozen_model.split('/')[-1]
                model_name = model.split('.pb')[0]
                print(model_name)
                converter.convert(model_name + '.tflex', flags.device, flags.level)
        else:
            print('--input_arrays and --output_arrays are required.')
    elif flags.keras_model:
        converter = tflex.Converter.from_keras_model(flags.keras_model)
        if flags.path_name:
            converter.convert(flags.path_name, flags.device, flags.level)
        else:
            model = flags.keras_model.split('/')[-1]
            model_name = model.split('.h5')[0]
            converter.convert(model_name + '.tflex', flags.device, flags.level)
    elif flags.saved_model:
        converter = tflex.Converter.from_saved_model(flags.saved_model)
        if flags.path_name:
            converter.convert(flags.path_name, flags.device, flags.level)
        else:
            model_name = flags.saved_model.split('/')[-2]
            converter.convert(model_name + '.tflex', flags.device, flags.level)
    else:
        subprocess.call(['tflexconverter -h'], shell=True)


if __name__ == '__main__':
    main()
