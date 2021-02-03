#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np

from .agent_data import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomData:
    time_unit_factor_seconds: float
    spatial_unit_factor_meters: float
    box_size: np.ndarray
    agent_data: AgentData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        box_size: np.ndarray,
        agent_data: AgentData,
        time_unit_factor_seconds: float = 1.0,
        spatial_unit_factor_meters: float = 1.0,
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
        time_unit_factor_seconds : float (optional)
            A float multiplier needed to convert temporal data
            (e.g. timeStepSize) to seconds
            ex: 1e-9 if times are in nanoseconds
            Default: 1.0
        spatial_unit_factor_meters : float (optional)
            A float multiplier needed to convert spatial data
            (including positions, radii, and box size) to meters
            ex: 1e-9 if distances are in nanometers
            Default: 1.0
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.time_unit_factor_seconds = time_unit_factor_seconds
        self.spatial_unit_factor_meters = spatial_unit_factor_meters
        self.box_size = box_size
        self.agent_data = agent_data
        self.plots = plots
