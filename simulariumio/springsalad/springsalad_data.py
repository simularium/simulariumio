#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import CameraData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SpringsaladData:
    path_to_sim_view_txt: str
    display_names: Dict[str, str]
    camera_defaults: CameraData
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        path_to_sim_view_txt: str,
        display_names: Dict[str, str] = {},
        camera_defaults: CameraData = CameraData(),
        scale_factor: float = 1.0,
        plots: List[Dict[str, Any]] = [],
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
        display_names : Dict[str, str] (optional)
            A mapping from molecule names in the sim view txt file
            to names to display in the Simularium Viewer
            Default: use names from sim view txt file
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
        self.display_names = display_names
        self.camera_defaults = camera_defaults
        self.scale_factor = scale_factor
        self.plots = plots
