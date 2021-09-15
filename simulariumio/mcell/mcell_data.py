#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class McellData:
    path_to_data_model_json: str
    path_to_binary_files: str
    meta_data: MetaData
    nth_timestep_to_read: int
    display_data: Dict[str, DisplayData]
    surface_mol_rotation_angle: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        path_to_data_model_json: str,
        path_to_binary_files: str,
        meta_data: MetaData = None,
        nth_timestep_to_read: int = 1,
        display_data: Dict[str, DisplayData] = None,
        surface_mol_rotation_angle: float = None,
        plots: List[Dict[str, Any]] = None,
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
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        nth_timestep_to_read: int (optional)
            Visualize every Nth timestep
            e.g. if 10, only every 10th timestep will be visualized
            Default: 1
        display_data: Dict[str, DisplayData] (optional)
            A mapping from molecule names in the MCell data
            to DisplayData, including names and display info
            to use for rendering this agent type in the Simularium Viewer
            Default: for names, use names from MCell,
                for radius, use value from MCell,
                for rendering, use default representations and colors
        surface_mol_rotation_angle: float (optional)
            The angle to use to calculate rotations
            around surface molecules' normals
            Default: use random angles
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.path_to_data_model_json = path_to_data_model_json
        self.path_to_binary_files = path_to_binary_files
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.nth_timestep_to_read = nth_timestep_to_read
        self.display_data = display_data if display_data is not None else {}
        self.surface_mol_rotation_angle = surface_mol_rotation_angle
        self.plots = plots if plots is not None else []
