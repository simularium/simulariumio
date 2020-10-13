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
    box_size: np.ndarray
    agent_data: AgentData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        box_size: np.ndarray,
        agent_data: AgentData,
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
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.box_size = box_size
        self.agent_data = agent_data
        self.plots = plots
