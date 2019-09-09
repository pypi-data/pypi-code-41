from __future__ import division
import numpy as np
import csv
import os
from os.path import join
import pkg_resources
from point_viz.utils import get_color_from_intensity, get_color_from_height, \
    create_dir, coors_normalize


class PointvizConverter(object):
    def __init__(self, home):
        self.home = home
        self.task_name = 'default'
        create_dir(self.home, clean=False)
        create_dir(join(self.home, 'data'), clean=False)
        create_dir(join(self.home, 'html'), clean=False)
        return_code = os.system("cp -r {} {}".format(pkg_resources.resource_filename('point_viz', 'src'), self.home))
        if return_code != 0:
            raise IOError("Error occurred when copying html template files, make sure the pip package has been "
                          "properly installed and you have authority to create: {}".format(self.home))

    def convert_pc_csv(self, task_name, coors, default_rgb, intensity):
        coors, norm = coors_normalize(coors)
        if default_rgb is not None:
            assert len(coors) == len(default_rgb)
            rgb = default_rgb
        elif intensity is not None:
            assert len(coors) == len(intensity)
            rgb = get_color_from_intensity(intensity)
        else:
            rgb = get_color_from_height(coors)

        head = ['x', 'y', 'z', 'r', 'g', 'b']
        output_csv = join(self.home, 'data', '{}_pc.csv'.format(task_name))

        with open(output_csv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=head)
            writer.writeheader()
            for i in range(len(coors)):
                x = coors[i, 0]
                y = coors[i, 1]
                z = coors[i, 2]
                r = rgb[i, 0]
                g = rgb[i, 1]
                b = rgb[i, 2]
                writer.writerow({'x': x, 'y': y, 'z': z, 'r': r, 'g': g, 'b': b})
        return norm

    def convert_bbox_csv(self, task_name, norm, bbox_params, bbox_color=True):
        head = ['label_text', 'color', 'l', 'h', 'w', 'x', 'y', 'z', 'r']
        output_csv = join(self.home, 'data', '{}_bbox.csv'.format(task_name))
        with open(output_csv, 'w') as f:
            writer = csv.DictWriter(f, fieldnames=head)
            writer.writeheader()
            for i in range(len(bbox_params)):
                bbox_param = bbox_params[i]
                assert 7 <= len(bbox_param) <= 9
                l = bbox_param[0] / norm
                h = bbox_param[1] / norm
                w = bbox_param[2] / norm
                x = bbox_param[3] / norm
                y = bbox_param[4] / norm
                z = bbox_param[5] / norm
                r = bbox_param[6]
                color = 'Magenta'
                label_text = ' '
                if len(bbox_param) == 8:
                    if bbox_color:
                        color = bbox_param[7].replace(" ", "").lower()
                    else:
                        label_text = bbox_param[7]
                elif len(bbox_param) == 9:
                    color = bbox_param[7].replace(" ", "").lower()
                    label_text = bbox_param[8]

                writer.writerow({'label_text': label_text,
                                 'color': color,
                                 'l': l, 'h': h, 'w': w,
                                 'x': x, 'y': y, 'z': z,
                                 'r': r})

    def compile(self, task_name, coors, default_rgb=None, intensity=None, bbox_params=None):
        if bbox_params is None:
            self.convert_pc_csv(task_name, coors, default_rgb, intensity)
            os.system("sed 's/TASK_NAME/{}/; s/INPUT_PC_CSV/{}/'  "
                      .format(task_name, task_name + '_pc.csv') +
                      "{} > ".format(join(self.home, 'src', 'template.html')) +
                      "{}".format(join(self.home, 'html', task_name + '.html')))
        elif coors is not None:
            norm = self.convert_pc_csv(task_name, coors, default_rgb, intensity)
            self.convert_bbox_csv(task_name, norm, bbox_params)
            os.system("sed  's/TASK_NAME/{}/; s/INPUT_PC_CSV/{}/; s/INPUT_BBOX_CSV/{}/' "
                      .format(task_name, task_name + '_pc.csv', task_name + '_bbox.csv') +
                      "{} > ".format(join(self.home, 'src', 'template.html')) +
                      "{}".format(join(self.home, 'html', task_name + '.html')))

        else:
            norm = np.max(np.abs(bbox_params[:, 3:6]))
            self.convert_bbox_csv(task_name, norm, bbox_params)
            os.system("sed 's/TASK_NAME/{}/; s/INPUT_BBOX_CSV/{}/'  "
                      .format(task_name, task_name + '_bbox.csv') +
                      "{} > ".format(join(self.home, 'src', 'template.html')) +
                      "{}".format(join(self.home, 'html', task_name + '.html')))

