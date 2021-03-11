#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ..data_objects import TrajectoryData
from .filter import Filter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MultiplySpaceFilter(Filter):
    multiplier: float

    def __init__(
        self,
        multiplier: float,
    ):
        """
        This filter scales all spatial data by a supplied multiplier

        Parameters
        ----------
        multiplier : float
            float by which to multiply spatial values
        """
        self.multiplier = multiplier

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Multiply spatial values in the data
        """
        print(
            f"Filtering: multiplying spatial scale by {self.multiplier} -------------"
        )
        data.meta_data.box_size = self.multiplier * data.meta_data.box_size
        data.agent_data.positions = self.multiplier * data.agent_data.positions
        data.agent_data.radii = self.multiplier * data.agent_data.radii
        data.agent_data.subpoints = self.multiplier * data.agent_data.subpoints
        data.spatial_units.multiply(1.0 / self.multiplier)
        return data
