#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import UnitData, MetaData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellData:
    timestep: float
    path_to_output_dir: str
    meta_data: MetaData
    display_data: Dict[int, DisplayData]
    phase_names: Dict[int, Dict[int, str]]
    time_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        timestep: float,
        path_to_output_dir: str,
        meta_data: MetaData = None,
        display_data: Dict[int, DisplayData] = None,
        phase_names: Dict[int, Dict[int, str]] = None,
        time_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from PhysiCell (http://physicell.org/)
        and plot data

        Parameters
        ----------
        timestep : float
            A float amount of time that passes each step
        path_to_output_dir : string
            A string path to the PhysiCell output directory
            containing MultiCellDS XML and MATLAB files
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        display_data : Dict[int, DisplayData] (optional)
            The cell type ID from PhysiCell data mapped
            to DisplayData, including names and display info
            to use for rendering that agent type in the Simularium Viewer
            Default: for names, "cell[cell type ID from PhysiCell data]",
                for radius, calculate from cell's volume,
                for rendering, use default representations and colors
        phase_names : Dict[int, Dict[int, str]] (optional)
            the cell type ID from PhysiCell data mapped
            to display names for phases of that type
            Default: "phase[cell phase ID from PhysiCell data]"
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.timestep = timestep
        self.path_to_output_dir = path_to_output_dir
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.phase_names = phase_names if phase_names is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.plots = plots if plots is not None else []
