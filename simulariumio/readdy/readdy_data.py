#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import UnitData, MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReaddyData:
    meta_data: MetaData
    timestep: float
    path_to_readdy_h5: str
    radii: Dict[str, float]
    ignore_types: List[str]
    type_grouping: Dict[str, List[str]]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        timestep: float,
        path_to_readdy_h5: str,
        radii: Dict[str, float] = None,
        ignore_types: List[str] = None,
        type_grouping: Dict[str, List[str]] = None,
        time_units: UnitData = UnitData("s"),
        spatial_units: UnitData = UnitData("m"),
        plots: List[Dict[str, Any]] = [],
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
        radii : Dict[str, float] (optional)
            A mapping of ReaDDy particle type to radius
            of each visualized sphere for that type
            Default: 1.0 (for each particle)
        ignore_types : List[str] (optional)
            A list of string ReaDDy particle types to ignore
        type_grouping : Dict[str, List[str]] (optional)
            A mapping of a new group type name to a list of
            ReaDDy particle types to include in that group
            e.g. {"moleculeA":["A1","A2","A3"]}
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
        self.radii = radii
        self.ignore_types = ignore_types
        self.type_grouping = type_grouping
        self.time_units = time_units
        self.spatial_units = spatial_units
        self.plots = plots
