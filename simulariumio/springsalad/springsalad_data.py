#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import CameraData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SpringsaladData:
    path_to_sim_view_txt: str
    display_data: Dict[str, DisplayData]
    camera_defaults: CameraData
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        path_to_sim_view_txt: str,
        display_data: Dict[str, DisplayData] = None,
        camera_defaults: CameraData = None,
        scale_factor: float = 1.0,
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
        display_data: Dict[str, DisplayData] (optional)
            The particle type name from SpringSaLaD data mapped
            to display names and rendering info for that type,
            Default: for names, use names from sim view txt file,
                for radius, use value from SpringSaLaD,
                for rendering, use default representations and colors
        camera_defaults : CameraData (optional)
            camera's initial settings
            which it also returns to when reset
            Default: CameraData()
        scale_factor : float (optional)
            A multiplier for the scene, use if
            visualization is too large or small
            Default: 1.0
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.path_to_sim_view_txt = path_to_sim_view_txt
        self.display_data = display_data if display_data is not None else {}
        self.camera_defaults = (
            camera_defaults if camera_defaults is not None else CameraData()
        )
        self.scale_factor = scale_factor
        self.plots = plots if plots is not None else []
