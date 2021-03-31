#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import UnitData, MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SpringsaladData:
    path_to_sim_view_txt: str
    camera_defaults: CameraData
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        path_to_sim_view_txt: str,
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
        camera_defaults: CameraData (optional)
            camera's initial settings
            which it also returns to when reset
            Default: CameraData(
                position=[0,0,120],
                look_at_position=[0,0,0],
                up_vector=[0,1,0],
                fov_degrees=50
            )
        scale_factor : float (optional)
            A multiplier for the scene, use if
            visualization is too large or small
            Default: 1.0
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.path_to_sim_view_txt = path_to_sim_view_txt
        self.camera_defaults = camera_defaults
        self.scale_factor = scale_factor
        self.plots = plots
