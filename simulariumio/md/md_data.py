#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from MDAnalysis import Universe

from ..data_objects import MetaData, UnitData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MdData:
    md_universe: Universe
    nth_timestep_to_read: int
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        md_universe: Universe,
        nth_timestep_to_read: int = 1,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from molecular dynamics models

        Parameters
        ----------
        timestep : float
            A float amount of time in seconds that passes each step
        md_universe: Universe
            A MDAnalysis Universe object containing MD trajectory data.
            See MDAnalysis package documentation for how to create one
            (https://docs.mdanalysis.org/stable/documentation_pages/core/universe.html)
        nth_timestep_to_read: int (optional)
            Visualize every Nth timestep
            e.g. if 10, only every 10th timestep will be visualized
            Default: 1
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        display_data: Dict[str, DisplayData] (optional)
            The element abbreviation mapped
            to display name and rendering info for that type,
            Default: for names, use element abbreviation,
                for radius, use 1.0,
                for rendering, use colors from Jmol and default representations
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
        self.md_universe = md_universe
        self.nth_timestep_to_read = nth_timestep_to_read
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
