#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import (
    MetaData,
    UnitData,
    DisplayData,
)

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class UsdData:
    usd_file_path: str
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]
    center: bool

    def __init__(
        self,
        usd_file_path: str,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
        center: bool = True,
    ):
        """
        This object holds simulation trajectory outputs
        from USD (Universal Scene Description) files

        Parameters
        ----------
        usd_file_path: str
            Path to the .usd, .usda, or .usdc file.
            Must be a file path (not contents) because
            the USD library requires file-based access.
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        display_data: Dict[str, DisplayData] (optional)
            The mesh prim name from USD data mapped
            to display names and rendering info for that type.
            Default: auto-detect from USD mesh and material data
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            Default: 1.0 meter
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        center : bool (optional)
            If true, the spatial values of the data are centered
            around the origin (0, 0, 0) during conversion
            Default: True
        """
        self.usd_file_path = usd_file_path
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
        self.center = center
