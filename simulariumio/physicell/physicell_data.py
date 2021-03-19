#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import UnitData, MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellData:
    meta_data: MetaData
    timestep: float
    time_units: UnitData
    path_to_output_dir: str
    types: Dict[int, Dict[Any, str]]
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        timestep: float,
        path_to_output_dir: str,
        types: Dict[int, Dict[Any, str]] = None,
        time_units: UnitData = UnitData("s"),
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        from PhysiCell (http://physicell.org/)
        and plot data

        Parameters
        ----------
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        timestep : float
            A float amount of time that passes each step
        path_to_output_dir : string
            A string path to the PhysiCell output directory
            containing MultiCellDS XML and MATLAB files
        types : Dict[int, Dict[Any, str]] (optional)
            the cell type ID from PhysiCell data mapped
            to display name for that type, and display names
            for phases of that type
            "name" or [cell phase ID from PhysiCell data] : str
                "name" or the cell phase ID from PhysiCell data mapped
                to the display names
                Default: "cell[cell type ID from PhysiCell data]#
                    phase[cell phase ID from PhysiCell data]"
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.meta_data = meta_data
        self.timestep = timestep
        self.path_to_output_dir = path_to_output_dir
        self.types = types
        self.time_units = time_units
        self.plots = plots
