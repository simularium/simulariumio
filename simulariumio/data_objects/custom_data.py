#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np

from .agent_data import AgentData
from .unit_data import UnitData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomData:
    box_size: np.ndarray
    agent_data: AgentData
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        box_size: np.ndarray,
        agent_data: AgentData,
        time_units: UnitData = UnitData("s"),
        spatial_units: UnitData = UnitData("m"),
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds custom simulation trajectory outputs
        and plot data

        Parameters
        ----------
        box_size : np.ndarray (shape = [3])
            A numpy ndarray containing the XYZ dimensions
            of the simulation bounding volume
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
        self.box_size = box_size
        self.agent_data = agent_data
        self.time_units = time_units
        self.spatial_units = spatial_units
        self.plots = plots

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """"""
        return cls(
            box_size=np.array([
                float(buffer_data["trajectoryInfo"]["size"]["x"]),
                float(buffer_data["trajectoryInfo"]["size"]["y"]),
                float(buffer_data["trajectoryInfo"]["size"]["z"]),
            ]),
            agent_data=AgentData.from_buffer_data(buffer_data),
            time_units=UnitData(
                buffer_data["trajectoryInfo"]["timeUnits"]["name"], 
                float(buffer_data["trajectoryInfo"]["timeUnits"]["magnitude"]),
            ),
            spatial_units=UnitData(
                buffer_data["trajectoryInfo"]["spatialUnits"]["name"], 
                float(buffer_data["trajectoryInfo"]["spatialUnits"]["magnitude"]),
            ),
            plots=buffer_data["plotData"]["data"]
        )
