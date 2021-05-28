#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict
import logging

import numpy as np

from ..data_objects import TrajectoryData
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
                tid = int(data.agent_data.type_ids[t][n])
                if tid in self.type_id_mapping:
                    tid = self.type_id_mapping[tid]
                type_ids[t][n] = tid
        data.agent_data.type_ids = type_ids
        return data
