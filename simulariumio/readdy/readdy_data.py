#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import UnitData, MetaData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReaddyData:
    meta_data: MetaData
    timestep: float
    path_to_readdy_h5: str
    display_info: Dict[str, DisplayData]
    ignore_types: List[str]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        timestep: float,
        path_to_readdy_h5: str,
        display_info: Dict[str, DisplayData] = None,
        ignore_types: List[str] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from ReaDDy (https://readdy.github.io/)
        and plot data

        Parameters
        ----------
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        timestep : float
            A float amount of time in seconds that passes each step
            Default: 0.0
        path_to_readdy_h5 : str
            A string path to the ReaDDy trajectory file (.h5)
        display_info : Dict[str, DisplayData] (optional)
            The cell type name from ReaDDy data mapped
            to display names and rendering info for that type,
            Default: for names, use ReaDDy name,
                for rendering, use default representations and colors
        ignore_types : List[str] (optional)
            A list of string ReaDDy particle types to ignore
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
        self.timestep = timestep
        self.path_to_readdy_h5 = path_to_readdy_h5
        self.display_info = display_info if display_info is not None else {}
        self.ignore_types = ignore_types
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = spatial_units if time_units is not None else UnitData("m")
        self.plots = plots if plots is not None else []
