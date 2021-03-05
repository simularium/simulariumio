#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from typing import Dict
import logging

import numpy as np

from ..data_objects import TrajectoryData, AgentData
from .filter import Filter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReorderAgentsFilter(Filter):
    type_id_mapping: Dict[int, int]

    def __init__(self, type_id_mapping: Dict[int, int]):
        """
        This object contains parameters for changing the type IDs
        of the agents, so that the agents are listed
        and colored in a different order

        Parameters
        ----------
        type_id_mapping : Dict[int, int]
            change each int key type ID in the data to
            the given int value
        """
        self.type_id_mapping = type_id_mapping

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Change the type IDs of the agents, so that the agents are listed
        and colored in a different order
        """
        print("Filtering: reorder agents -------------")
        # get dimensions
        total_steps = data.agent_data.times.size
        max_agents = int(np.amax(data.agent_data.n_agents))
        # get filtered data
        type_ids = np.zeros((total_steps, max_agents))
        for t in range(data.agent_data.times.size):
            for n in range(int(data.agent_data.n_agents[t])):
                tid = data.agent_data.type_ids[t][n]
                if tid in self.type_id_mapping:
                    tid = self.type_id_mapping[tid]
                type_ids[t][n] = tid
        return TrajectoryData(
            box_size=np.copy(data.box_size),
            agent_data=AgentData(
                times=np.copy(data.agent_data.times),
                n_agents=np.copy(data.agent_data.n_agents),
                viz_types=np.copy(data.agent_data.viz_types),
                unique_ids=np.copy(data.agent_data.unique_ids),
                types=copy.copy(data.agent_data.types),
                positions=np.copy(data.agent_data.positions),
                radii=np.copy(data.agent_data.radii),
                n_subpoints=np.copy(data.agent_data.n_subpoints),
                subpoints=np.copy(data.agent_data.subpoints),
                draw_fiber_points=data.agent_data.draw_fiber_points,
                type_ids=type_ids,
            ),
            time_units=copy.copy(data.time_units),
            spatial_units=copy.copy(data.spatial_units),
            plots=copy.copy(data.plots),
        )
