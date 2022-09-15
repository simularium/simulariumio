#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
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
        new_n_subpoints = np.zeros((total_steps, max_agents))
        new_subpoints = np.zeros((total_steps, max_agents, max_subpoints))
        for time_index in range(total_steps):
            for agent_index in range(int(data.agent_data.n_agents[time_index])):
                sp_items = self.get_items_from_subpoints(
                    data.agent_data, time_index, agent_index
                )
                if sp_items is None:
                    continue
                # get the increment to use for this type
                type_name = data.agent_data.types[time_index][agent_index]
                if type_name in self.n_per_type:
                    inc = self.n_per_type[type_name]
                else:
                    inc = self.default_n
                new_n_items = math.ceil(sp_items.shape[0] / float(inc))
                new_n_sp = sp_items.shape[1] * new_n_items
                new_n_subpoints[time_index][agent_index] = new_n_sp
                new_subpoints[time_index][agent_index][:new_n_sp] = sp_items[
                    ::inc
                ].flatten()
        data.agent_data.n_subpoints = new_n_subpoints
        data.agent_data.subpoints = new_subpoints
        print(
            f"filtered dims = {total_steps} timesteps X "
            f"{max_agents} agents X {int(np.amax(new_n_subpoints))} subpoints"
        )
        return data
