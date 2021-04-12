#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, UnitData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SmoldynData:
    meta_data: MetaData
    path_to_output_txt: str
    radii: Dict[str, float]
    display_names: Dict[str, str]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        path_to_output_txt: str,
        radii: Dict[str, float],
        display_names: Dict[str, str] = {},
        time_units: UnitData = UnitData("s"),
        spatial_units: UnitData = UnitData("m"),
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        from Smoldyn (http://www.smoldyn.org) and plot data

        Parameters
        ----------
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        path_to_output_txt : str
            A string path to the output txt file
            Generate by adding to your config.txt file:
                `output_files output.txt
                `cmd n 1 executiontime output.txt`
                `cmd n 1 listmols output.txt`
        radii : Dict[str,float] (optional)
            A mapping of type names to the radii
            with which to draw them
            Default : 1.0 for any type name not specified
        display_names : Dict[str, str] (optional)
            A mapping from original species names
            to names to display in the Simularium Viewer
            Default: use original names
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            (including positions, radii, and box size)
            Default: 1.0 meter
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.meta_data = meta_data
        self.path_to_output_txt = path_to_output_txt
        self.radii = radii
        self.display_names = display_names
        self.time_units = time_units
        self.spatial_units = spatial_units
        self.plots = plots
