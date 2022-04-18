#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simulariumio.data_objects.agent_data import AgentData
from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthAgentFilter(Filter):
    n_per_type: Dict[str, int]
    default_n: int

    def __init__(self, n_per_type: Dict[str, int], default_n: int = 1):
        """
        This filter reduces the number of agents in each frame
        of simularium data by filtering out all but every nth agent

        Parameters
        ----------
        n_per_type : Dict[str, int]
            N for agents of each type,
            keep every nth agent of that type, filter out all the others
        default_n : int (optional)
            N for any agents of type not specified in n_per_type
            Default: 1
        """
        self.n_per_type = n_per_type
        self.default_n = default_n

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Reduce the number of agents in each frame of the simularium
        data by filtering out all but every nth agent
        """
        print("Filtering: every Nth agent -------------")
        # get filtered data
        start_dimensions = data.agent_data.get_dimensions()
        result = AgentData.from_dimensions(start_dimensions)
        result.times = data.agent_data.times
        result.draw_fiber_points = data.agent_data.draw_fiber_points
        result.display_data = data.agent_data.display_data
        for time_index in range(start_dimensions.total_steps):
            new_agent_index = 0
            n_found = {}
            n_a = int(data.agent_data.n_agents[time_index])
            for agent_index in range(n_a):
                type_name = str(data.agent_data.types[time_index][agent_index])
                if type_name not in n_found:
                    n_found[type_name] = -1
                n_found[type_name] += 1
                if type_name in self.n_per_type:
                    inc = self.n_per_type[type_name]
                else:
                    inc = self.default_n
                if inc < 1 or n_found[type_name] % inc != 0:
                    continue
                result.viz_types[time_index][
                    new_agent_index
                ] = data.agent_data.viz_types[time_index][agent_index]
                result.unique_ids[time_index][
                    new_agent_index
                ] = data.agent_data.unique_ids[time_index][agent_index]
                result.types[time_index].append(
                    data.agent_data.types[time_index][agent_index]
                )
                result.positions[time_index][
                    new_agent_index
                ] = data.agent_data.positions[time_index][agent_index]
                result.radii[time_index][new_agent_index] = data.agent_data.radii[
                    time_index
                ][agent_index]
                result.rotations[time_index][
                    new_agent_index
                ] = data.agent_data.rotations[time_index][agent_index]
                result.n_subpoints[time_index][
                    new_agent_index
                ] = data.agent_data.n_subpoints[time_index][agent_index]
                result.subpoints[time_index][new_agent_index][
                    : np.shape(data.agent_data.subpoints[time_index][agent_index])[0]
                ] = data.agent_data.subpoints[time_index][agent_index]
                new_agent_index += 1
            result.n_agents[time_index] = new_agent_index
        data.agent_data = result
        print(
            f"filtered dims = {start_dimensions.total_steps} timesteps X "
            f"{int(np.amax(result.n_agents))} agents X "
            f"{int(np.amax(data.agent_data.n_subpoints))} subpoints"
        )
        return data
