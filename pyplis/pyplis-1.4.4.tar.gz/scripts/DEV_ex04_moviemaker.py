# -*- coding: utf-8 -*-
#
# Pyplis is a Python library for the analysis of UV SO2 camera data
# Copyright (C) 2017 Jonas Gliss (jonasgliss@gmail.com)
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License a
# published by the Free Software Foundation, either version 3 of
# the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
Pyplis example script no. 4 - Prepare AA image list (from onband list)

Script showing how to work in AA mode using ImgList object
"""
# Check script version
from SETTINGS import check_version

check_version()

import pyplis
from matplotlib.pyplot import close, pause, Line2D
from matplotlib.patches import Circle
from os.path import join
from matplotlib.pyplot import rcParams

rcParams["font.size"] = 15
rcParams["axes.labelsize"] = 15
### IMPORT GLOBAL SETTINGS
from SETTINGS import SAVE_DIR, IMG_DIR

### IMPORTS FROM OTHER EXAMPLE SCRIPTS
from ex01_analysis_setup import create_dataset
from ex02_meas_geometry import find_viewing_direction

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.animation as manimation


### SCRIPT FUNCTION DEFINITIONS
def prepare_aa_image_list(bg_corr_mode=6):
    """Get and prepare onband list for aa image mode
    
    The relevant gas free areas for background image modelling are set 
    automatically (see also ex. 3 for details)
    
    :return: - on list in AA mode    
    """

    dataset = create_dataset()
    geom, _ = find_viewing_direction(dataset.meas_geometry, False)

    ### Set plume background images for on and off
    # this is the same image which is also used for example script NO
    # demonstrating the plume background routines
    path_bg_on = join(IMG_DIR,
                      'EC2_1106307_1R02_2015091607022602_F01_Etna.fts')
    path_bg_off = join(IMG_DIR,
                       'EC2_1106307_1R02_2015091607022820_F02_Etna.fts')

    ### Get on and off lists and activate dark correction
    lst = dataset.get_list("on")
    lst.activate_darkcorr()  # same as lst.darkcorr_mode = 1

    off_list = dataset.get_list("off")
    off_list.activate_darkcorr()

    # Prepare on and offband background images
    bg_on = pyplis.Img(path_bg_on)
    bg_on.subtract_dark_image(lst.get_dark_image())

    bg_off = pyplis.Img(path_bg_off)
    bg_off.subtract_dark_image(off_list.get_dark_image())

    # set the background images within the lists
    lst.set_bg_img(bg_on)
    off_list.set_bg_img(bg_off)

    # automatically set gas free areas
    lst.bg_model.guess_missing_settings(lst.current_img())
    # Now update some of the information from the automatically set sky ref
    # areas
    lst.bg_model.xgrad_line_startcol = 20
    lst.bg_model.xgrad_line_rownum = 25
    off_list.bg_model.xgrad_line_startcol = 20
    off_list.bg_model.xgrad_line_rownum = 25

    # set background modelling mode
    lst.bg_model.mode = bg_corr_mode
    off_list.bg_model.mode = bg_corr_mode

    lst.aa_mode = True  # activate AA mode

    lst.meas_geometry = geom
    return lst


def draw_flow(flow, ax, ext_fac=2, color="w"):
    lines = flow.calc_flow_lines(extend_len_fac=ext_fac)
    drawn = []
    for (x1, y1), (x2, y2) in lines:
        # =============================================================================
        #         ax.arrow(x1, y1, x2, y2, head_width=0.05, head_length=0.1,
        #                  fc='w', ec='w')
        # =============================================================================
        drawn.append(ax.add_artist(Line2D([x1, x2], [y1, y2],
                                          color=color)))
        drawn.append(ax.add_patch(Circle((x2, y2), 2,
                                         ec=color, fc=color)))
    return drawn


### SCRIPT MAIN FUNCTION
if __name__ == "__main__":
    close("all")
    aa_list = prepare_aa_image_list()

    FFMpegWriter = manimation.writers['ffmpeg']
    metadata = dict(title='Movie Test', artist='Matplotlib',
                    comment='Movie support!')

    aa_list.set_flow_images()
    flow = aa_list.optflow
    flow.roi_abs = [0, 0, 1344, 725]
    aa_list.optflow_mode = True

    ttot = 10.0  # s
    num = aa_list.nof
    fps = int(num / ttot)
    writer = FFMpegWriter(fps=fps, metadata=metadata)
    fig, ax = plt.subplots(1, 1, figsize=(18, 12), dpi=72)
    aa_list.this.show(vmin=-0.1, vmax=0.25, ax=ax, zlabel="AA")
    disp = ax.imshow(aa_list.this.img, vmin=-0.1, vmax=0.25)

    ax.set_title("")
    ax.set_title("Pyplis Etna testdata", loc="left")
    ax.set_title(aa_list.current_time().strftime("%d-%m-%Y %H:%M:%S"), loc="right")

    with writer.saving(fig, join(SAVE_DIR, "writer_test.mp4"), dpi=72):
        for i in range(num):
            disp.set_data(aa_list.this.img)
            d = draw_flow(flow, ax=ax)
            ax.set_title(aa_list.current_time().strftime("%d-%m-%Y %H:%M:%S"), loc="right")
            writer.grab_frame()
            pause(0.0001)
            aa_list.goto_next()
            for item in d:
                item.remove()
                del item
