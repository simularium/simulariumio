#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import UnitData, MetaData, AgentTypeInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellData:
    meta_data: MetaData
    timestep: float
    time_units: UnitData
    path_to_output_dir: str
    agent_info: Dict[int, AgentTypeInfo]
    phase_names: Dict[int, Dict[int, str]]
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        timestep: float,
        path_to_output_dir: str,
        agent_info: Dict[int, AgentTypeInfo] = None,
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
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        timestep : float
            A float amount of time that passes each step
        path_to_output_dir : string
            A string path to the PhysiCell output directory
            containing MultiCellDS XML and MATLAB files
        agent_info : Dict[int, AgentTypeInfo] (optional)
            The cell type ID from PhysiCell data mapped
            to display names and rendering info for that type,
            Default: for names, "cell[cell type ID from PhysiCell data]",
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
        self.meta_data = meta_data
        self.timestep = timestep
        self.path_to_output_dir = path_to_output_dir
        self.agent_info = agent_info if agent_info is not None else {}
        self.phase_names = phase_names if phase_names is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.plots = plots if plots is not None else []
