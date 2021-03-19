#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging
from typing import Any, Dict, List

from .agent_data import AgentData
from .unit_data import UnitData
from .meta_data import MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TrajectoryData:
    meta_data: MetaData
    agent_data: AgentData
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        agent_data: AgentData,
        time_units: UnitData = UnitData("s"),
        spatial_units: UnitData = UnitData("m"),
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        and plot data

        Parameters
        ----------
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        agent_data : AgentData
            An object containing data for each agent
            at each timestep
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            Default: 1.0 meter
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.meta_data = meta_data
        self.agent_data = agent_data
        self.time_units = time_units
        self.spatial_units = spatial_units
        self.plots = plots

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """
        Create TrajectoryData from a simularium JSON dict containing buffers
        """
        return cls(
            meta_data=MetaData.from_buffer_data(buffer_data),
            agent_data=AgentData.from_buffer_data(buffer_data),
            time_units=UnitData(
                buffer_data["trajectoryInfo"]["timeUnits"]["name"],
                float(buffer_data["trajectoryInfo"]["timeUnits"]["magnitude"]),
            ),
            spatial_units=UnitData(
                buffer_data["trajectoryInfo"]["spatialUnits"]["name"],
                float(buffer_data["trajectoryInfo"]["spatialUnits"]["magnitude"]),
            ),
            plots=buffer_data["plotData"]["data"],
        )

    def __deepcopy__(self, memo):
        result = type(self)(
            meta_data=copy.deepcopy(self.meta_data, memo),
            agent_data=copy.deepcopy(self.agent_data, memo),
            time_units=copy.copy(self.time_units),
            spatial_units=copy.copy(self.spatial_units),
            plots=copy.deepcopy(self.plots, memo),
        )
        return result
