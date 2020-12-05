#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np

from .agent_data import AgentData
from ..constants import SPATIAL_UNIT_OPTIONS
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomData:
    spatial_units: str
    box_size: np.ndarray
    agent_data: AgentData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        spatial_units: str,
        box_size: np.ndarray,
        agent_data: AgentData,
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds custom simulation trajectory outputs
        and plot data

        Parameters
        ----------
        spatial_units : str
            A string specifying the units for spatial data,
            which includes positions, box size, radii
            Options:
                Ym = yottameters
                Zm = zettameters
                Em = exameters
                Pm = petameters
                Tm = terameters
                Gm = gigameters
                Mm = megameters
                km = kilometers
                hm = hectometers
                dam = decameters
                m = meters
                dm = decimeters
                cm = centimeters
                mm = millimeters
                um or μm = micrometers (microns)
                nm = nanometers
                A = angstroms
                pm = picometers
                fm = femptometers
                am = attometers
                zm = zeptometers
                ym = yoctometers
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
        if spatial_units not in SPATIAL_UNIT_OPTIONS:
            raise DataError(f"Unrecognized spatial unit: {spatial_units}")
        self.spatial_units = spatial_units
        self.box_size = box_size
        self.agent_data = agent_data
        self.plots = plots
