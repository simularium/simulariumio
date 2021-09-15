#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import DisplayData, MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SpringsaladData:
    path_to_sim_view_txt: str
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        path_to_sim_view_txt: str,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from SpringSaLaD (https://vcell.org/ssalad)
        and plot data

        Parameters
        ----------
        path_to_sim_view_txt : str
            A string path to the txt file named
            "[model name]_SIM_VIEW_[run name].txt"
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        display_data: Dict[str, DisplayData] (optional)
            The particle type name from SpringSaLaD data mapped
            to display names and rendering info for that type,
            Default: for names, use names from sim view txt file,
                for radius, use value from SpringSaLaD,
                for rendering, use default representations and colors
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.path_to_sim_view_txt = path_to_sim_view_txt
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.plots = plots if plots is not None else []
