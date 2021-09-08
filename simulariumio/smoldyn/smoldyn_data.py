#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, UnitData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SmoldynData:
    meta_data: MetaData
    path_to_output_txt: str
    display_data: Dict[str, DisplayData]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        path_to_output_txt: str,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
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
        display_data: Dict[str, DisplayData] (optional)
            The particle type name from Smoldyn data mapped
            to display names and rendering info for that type,
            Default: for names, use Smoldyn name,
                for radius, use 1.0,
                for rendering, use default representations and colors
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
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
