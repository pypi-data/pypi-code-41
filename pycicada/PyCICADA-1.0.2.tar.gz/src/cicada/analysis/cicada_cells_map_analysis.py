from cicada.analysis.cicada_analysis import CicadaAnalysis
from cicada.utils.display.cells_map_utils import CellsCoord
import sys
from time import sleep, time
import numpy as np
from shapely.geometry import MultiPoint, LineString

class CicadaCellsMapAnalysis(CicadaAnalysis):
    def __init__(self):
        """
        """
        CicadaAnalysis.__init__(self, name="cells_map", family_id="display",
                                short_description="Plot map of the cells")

    def check_data(self):
        """
        Check the data given one initiating the class and return True if the data given allows the analysis
        implemented, False otherwise.
        :return: a boolean
        """
        super().check_data()

        if self._data_format != "nwb":
            self.invalid_data_help = "Non NWB format compatibility not yet implemented"
            return False

        for data in self._data_to_analyse:

            segmentations = data.get_segmentations()

            # we need at least one segmentation
            if (segmentations is None) or len(segmentations) == 0:
                self.invalid_data_help = "No segmentation data available"
                return False

        return True

    def set_arguments_for_gui(self):
        """

        Returns:

        """
        CicadaAnalysis.set_arguments_for_gui(self)

        # range_arg = {"arg_name": "psth_range", "value_type": "int", "min_value": 50, "max_value": 2000,
        #              "default_value": 500, "short_description": "Range of the PSTH (ms)"}
        # self.add_argument_for_gui(**range_arg)
        #
        # stim_arg = {"arg_name": "stimulus name", "value_type": "str",
        #              "default_value": "stim", "short_description": "Name of the stimulus"}
        # self.add_argument_for_gui(**stim_arg)
        #
        # plot_arg = {"arg_name": "plot_options", "choices": ["lines", "bars"],
        #             "default_value": "bars", "short_description": "Options to display the PSTH"}
        # self.add_argument_for_gui(**plot_arg)
        #
        cell_numbers_arg = {"arg_name": "with_cell_numbers", "value_type": "bool",
                            "default_value": True, "short_description": "Display cell numbers"}

        self.add_argument_for_gui(**cell_numbers_arg)

        format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
                      "default_value": "pdf", "short_description": "Formats in which to save the figures",
                      "multiple_choices": True}

        self.add_argument_for_gui(**format_arg)

        cells_color_arg = {"arg_name": "cells_color", "value_type": "color_with_alpha",
                           "default_value": (1, 1, 1, 1.), "short_description": "Cells' color"}
        self.add_argument_for_gui(**cells_color_arg)

        edge_color_arg = {"arg_name": "edge_color", "value_type": "color_with_alpha",
                          "default_value": (1, 1, 1, 1.), "short_description": "Cells' edge color"}
        self.add_argument_for_gui(**edge_color_arg)

        bg_color_arg = {"arg_name": "background_color", "value_type": "color_with_alpha",
                        "default_value": (0, 0, 0, 1.), "short_description": "Background color",
                        "long_description": "If calcium imaging movie background selected, the background won't matter"}
        self.add_argument_for_gui(**bg_color_arg)

        # dimgray is the default color
        cell_numbers_color_arg = {"arg_name": "cell_numbers_color", "value_type": "color",
                                  "default_value": (0.412, 0.412, 0.412, 1.), "short_description": "Cells' number color"}
        self.add_argument_for_gui(**cell_numbers_color_arg)

        welsh_arg = {"arg_name": "use_welsh_powell_coloring", "value_type": "bool",
                     "default_value": True, "short_description": "Use welsh powell algorithm to color cells",
                     "long_description": "If chosen, then groups of cells will be decide by the algorithm. "
                                         "As well as colors, "
                                         "except for isolated cell, whose color will be the cells' color choosen."}

        self.add_argument_for_gui(**welsh_arg)

        # avg_arg = {"arg_name": "average_fig", "value_type": "bool",
        #            "default_value": True, "short_description": "Add a figure that average all sessions"}
        #
        # self.add_argument_for_gui(**avg_arg)
        #
        # format_arg = {"arg_name": "save_formats", "choices": ["pdf", "png"],
        #             "default_value": "pdf", "short_description": "Formats in which to save the figures",
        #             "multiple_choices": True}
        #
        # self.add_argument_for_gui(**format_arg)


        segmentation_dict_for_arg = dict()
        for data in self._data_to_analyse:
            segmentation_dict_for_arg[data.identifier] = data.get_segmentations()
        # not mandatory, because one of the element will be selected by the GUI
        segmentation_arg = {"arg_name": "segmentation", "choices": segmentation_dict_for_arg,
                            "short_description": "Segmentation to use", "mandatory": False,
                            "multiple_choices": False}

        self.add_argument_for_gui(**segmentation_arg)

    def update_original_data(self):
        """
        To be called if the data to analyse should be updated after the analysis has been run.
        :return: boolean: return True if the data has been modified
        """
        pass

    def run_analysis(self, **kwargs):
        """
        test
        :param kwargs:
          segmentation

        :return:
        """
        CicadaAnalysis.run_analysis(self, **kwargs)

        start_time = time()
        n_sessions = len(self._data_to_analyse)

        segmentation_dict = kwargs['segmentation']

        with_cell_numbers = kwargs["with_cell_numbers"]

        save_formats = kwargs["save_formats"]
        if save_formats is None:
            save_formats = "pdf"

        cells_color = None
        if "cells_color" in kwargs:
            cells_color = kwargs["cells_color"]

        edge_color = None
        if "edge_color" in kwargs:
            edge_color = kwargs["edge_color"]

        background_color = None
        if "background_color" in kwargs:
            background_color = kwargs["background_color"]

        cell_numbers_color = None
        if "cell_numbers_color" in kwargs:
            cell_numbers_color = kwargs["cell_numbers_color"]

        use_welsh_powell_coloring = False
        if "use_welsh_powell_coloring" in kwargs:
            use_welsh_powell_coloring = kwargs['use_welsh_powell_coloring']

        for session_index, session_data in enumerate(self._data_to_analyse):
            session_identifier = session_data.identifier
            if isinstance(segmentation_dict, dict):
                segmentation_info = segmentation_dict[session_identifier]
            else:
                segmentation_info = segmentation_dict
            pixel_mask = session_data.get_pixel_mask(segmentation_info=segmentation_info)

            if pixel_mask is None:
                print(f"pixel_mask not available in for {session_data.identifier} "
                      f"in {segmentation_info}")
                self.update_progressbar(start_time, 100 / n_sessions)
                continue

            # TODO: use pixel_mask instead of using the coord of the contour of the cell
            #  means changing the way coord_cell works
            coord_list = []
            for cell in np.arange(len(pixel_mask)):
                pixels_coord = pixel_mask[cell]
                list_points_coord = [(pix[0], pix[1]) for pix in pixels_coord]
                convex_hull = MultiPoint(list_points_coord).convex_hull
                if isinstance(convex_hull, LineString):
                    coord_shapely = MultiPoint(list_points_coord).convex_hull.coords
                else:
                    coord_shapely = MultiPoint(list_points_coord).convex_hull.exterior.coords
                coord_list.append(np.array(coord_shapely).transpose())

            # TODO: get the real movie dimensions if available
            cells_coord = CellsCoord(coord_list, from_suite_2p=True)

            args_to_add = dict()
            if cells_color is not None:
                args_to_add["default_cells_color"] = cells_color
            if background_color is not None:
                args_to_add["background_color"] = background_color

            if edge_color is not None:
                args_to_add["default_edge_color"] = edge_color

            if cell_numbers_color is not None:
                args_to_add["cell_numbers_color"] = cell_numbers_color

            cells_coord.plot_cells_map(path_results=self.get_results_path(),
                                       data_id=session_identifier, show_polygons=False,
                                       fill_polygons=False,
                                       title_option="all_cells", connections_dict=None,
                                       use_welsh_powell_coloring=use_welsh_powell_coloring,
                                       cells_groups=None,
                                       cells_groups_colors=None,
                                       img_on_background=None,
                                       cells_groups_edge_colors=None,
                                       with_edge=True, cells_groups_alpha=None,
                                       dont_fill_cells_not_in_groups=False,
                                       with_cell_numbers=with_cell_numbers, save_formats=save_formats,
                                       save_plot=True, return_fig=False, **args_to_add)

            self.update_progressbar(start_time, 100 / n_sessions)

