#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging

import numpy as np

from ..data_objects import TrajectoryData, AgentData, UnitData, MetaData
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
        This filter multiplies spatial scale

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
        return TrajectoryData(
            meta_data=MetaData(
                box_size=self.multiplier * np.copy(data.meta_data.box_size)
            ),
            agent_data=AgentData(
                times=np.copy(data.agent_data.times),
                n_agents=np.copy(data.agent_data.n_agents),
                viz_types=np.copy(data.agent_data.viz_types),
                unique_ids=np.copy(data.agent_data.unique_ids),
                types=copy.copy(data.agent_data.types),
                positions=self.multiplier * np.copy(data.agent_data.positions),
                radii=self.multiplier * np.copy(data.agent_data.radii),
                n_subpoints=np.copy(data.agent_data.n_subpoints),
                subpoints=self.multiplier * np.copy(data.agent_data.subpoints),
                draw_fiber_points=data.agent_data.draw_fiber_points,
                type_ids=np.copy(data.agent_data.type_ids),
            ),
            time_units=copy.copy(data.time_units),
            spatial_units=UnitData(
                data.spatial_units.name, data.spatial_units.magnitude / self.multiplier
            ),
            plots=copy.copy(data.plots),
        )
