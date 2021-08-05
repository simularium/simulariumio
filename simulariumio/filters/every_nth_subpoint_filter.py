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
    n_per_type: Dict[str, int]
    default_n: int

    def __init__(self, n_per_type: Dict[str, int], default_n: int = 1):
        """
        This filter reduces the number of subpoints in each frame
        of simularium data

        Parameters
        ----------
        n_per_type : Dict[str, int]
            N for agents of each type,
            keep every nth subpoint for that type (if subpoints exist),
            filter out all the others
        default_n : int (optional)
            N for any agents of type not specified in n_per_type
            Default: 1
        """
        self.n_per_type = n_per_type
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
        for time_index in range(total_steps):
            for agent_index in range(int(data.agent_data.n_agents[time_index])):
                new_subpoint_index = 0
                if data.agent_data.n_subpoints[time_index][agent_index] > 0:
                    type_name = data.agent_data.types[time_index][agent_index]
                    if type_name in self.n_per_type:
                        inc = self.n_per_type[type_name]
                    else:
                        inc = self.default_n
                    for subpoint_index in range(
                        int(data.agent_data.n_subpoints[time_index][agent_index])
                    ):
                        if subpoint_index % inc != 0:
                            continue
                        subpoints[time_index][agent_index][
                            new_subpoint_index
                        ] = data.agent_data.subpoints[time_index][agent_index][
                            subpoint_index
                        ]
                        new_subpoint_index += 1
                n_subpoints[time_index][agent_index] = new_subpoint_index
        data.agent_data.n_subpoints = n_subpoints
        data.agent_data.subpoints = subpoints
        print(
            f"filtered dims = {total_steps} timesteps X "
            f"{max_agents} agents X {int(np.amax(n_subpoints))} subpoints"
        )
        return data
