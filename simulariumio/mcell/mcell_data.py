#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import CameraData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class McellData:
    path_to_data_model_json: str
    path_to_binary_files: str
    nth_timestep_to_read: int
    display_names: Dict[str, str]
    camera_defaults: CameraData
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        path_to_data_model_json: str,
        path_to_binary_files: str,
        nth_timestep_to_read: int = 1,
        display_names: Dict[str, str] = {},
        camera_defaults: CameraData = CameraData(),
        scale_factor: float = 1.0,
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        from MCell (https://mcell.org/)
        and plot data

        Parameters
        ----------
        path_to_data_model_json : str
            A string path to the json file
            containing the data model
        path_to_binary_files : str
            A string path to the directory containing
            visualization .dat binary files
        nth_timestep_to_read: int (optional)
            Visualize every Nth timestep
            e.g. if 10, only every 10th timestep will be visualized
            Default: 1
        display_names : Dict[str, str] (optional)
            A mapping from molecule names in the sim view txt file
            to names to display in the Simularium Viewer
            Default: use names from sim view txt file
        camera_defaults : CameraData (optional)
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
        self.path_to_data_model_json = path_to_data_model_json
        self.path_to_binary_files = path_to_binary_files
        self.nth_timestep_to_read = nth_timestep_to_read
        self.display_names = display_names
        self.camera_defaults = camera_defaults
        self.scale_factor = scale_factor
        self.plots = plots
