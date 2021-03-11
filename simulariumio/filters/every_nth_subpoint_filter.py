#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthSubpointFilter(Filter):
    n_per_type_id: Dict[int, int]
    default_n: int

    def __init__(self, n_per_type_id: Dict[int, int], default_n: int = 1):
        """
        This filter reduces the number of subpoints in each frame
        of simularium data

        Parameters
        ----------
        n_per_type_id : Dict[int, int]
            N for agents of each type ID,
            keep every nth subpoint for that type ID (if subpoints exist),
            filter out all the others
        default_n : int (optional)
            N for any agents of type not specified in n_per_type_id
            Default: 1
        """
        self.n_per_type_id = n_per_type_id
        self.default_n = default_n

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Reduce the number of subpoints in each frame of the simularium
        data by filtering out all but every nth subpoint
        """
        print("Filtering: every Nth subpoint -------------")
        # get dimensions
        total_steps = data.agent_data.times.size
        max_agents = int(np.amax(data.agent_data.n_agents))
        max_subpoints = int(np.amax(data.agent_data.n_subpoints))
        # get filtered data
        n_subpoints = np.zeros((total_steps, max_agents))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        for t in range(total_steps):
            for n in range(int(data.agent_data.n_agents[t])):
                i = 0
                if data.agent_data.n_subpoints[t][n] > 0:
                    type_id = data.agent_data.type_ids[t][n]
                    if type_id in self.n_per_type_id:
                        inc = self.n_per_type_id[type_id]
                    else:
                        inc = self.default_n
                    for s in range(int(data.agent_data.n_subpoints[t][n])):
                        if s % inc != 0:
                            continue
                        subpoints[t][n][i] = data.agent_data.subpoints[t][n][s]
                        i += 1
                n_subpoints[t][n] = i
        data.agent_data.n_subpoints = n_subpoints
        data.agent_data.subpoints = subpoints
        print(
            f"filtered dims = {total_steps} timesteps X "
            f"{max_agents} agents X {int(np.amax(n_subpoints))} subpoints"
        )
        return data
