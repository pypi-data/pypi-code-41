# -*- coding: utf-8 -*-
"""
automatically registers, derotates and box-crops images,
by Christian C. Sachs, uses molyso's registration functionality ( https://github.com/modsim/molyso )
https://dx.doi.org/10.1371/journal.pone.0163453
and a boxdetection routine from https://github.com/csachs/mfisp-boxdetection
"""

from molyso.imageio.imagestack import MultiImageStack
try:
    from molyso.imageio.imagestack_ometiff import OMETiffStack
    from molyso.imageio.imagestack_czi import CziStack
    from molyso.imageio.imagestack_nd2 import ND2Stack
except ImportError:
    pass

import argparse
import numpy

from tifffile import TiffWriter

from molyso.generic.registration import translation_2x1d, shift_image
from molyso.generic.rotation import find_rotation, rotate_image

from mfisp_boxdetection import find_box

def main():
    parser = argparse.ArgumentParser(
        description="boxcrop tool [using techniques of https://dx.doi.org/10.1371/journal.pone.0163453 ]"
    )

    parser.add_argument("input", type=str, help="input file name")
    parser.add_argument("--output", type=str, default="", help="output file name")
    parser.add_argument("--channel", type=int, default=0, help="bright field channel")

    args = parser.parse_args()
    if args.output == '':
        args.output = args.input + '_registered-%04d.tif'

    ims = MultiImageStack.open(args.input)

    mp = ims.get_meta('multipoints')

    channels = ims.get_meta('channels')

    bright_field_channel = args.channel

    for p in range(mp):
        first = ims.get_image(t=0, pos=p, channel=bright_field_channel)

        angle = find_rotation(first)

        rotated = rotate_image(first, angle)

        top, bottom, left, right = find_box(rotated, subsample=1, debug=False)

        first_box = rotated[top:bottom, left:right]

        buffer = numpy.zeros((channels,) + first_box.shape, dtype=first.dtype)

        try:
            output_name = args.output % p
        except TypeError:
            output_name = args.output

        with TiffWriter(output_name, imagej=True) as tiff:
            for t in range(ims.get_meta('timepoints')):

                current = ims.get_image(t=t, pos=p, channel=bright_field_channel)
                shift, = translation_2x1d(first, current)

                for c in range(channels):
                    if c == bright_field_channel:
                        shifted = shift_image(current, shift, background='blank')
                    else:
                        shifted = shift_image(ims.get_image(t=t, pos=p, channel=c), shift, background='blank')

                    rotated = rotate_image(shifted, angle)

                    buffer[c, :, :] = rotated[top:bottom, left:right]

                tiff.save(buffer)


if __name__ == '__main__':
    main()
