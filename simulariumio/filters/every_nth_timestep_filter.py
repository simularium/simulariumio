#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
from simulariumio.data_objects.dimension_data import DimensionData
from simulariumio.data_objects.agent_data import AgentData

import numpy as np

from ..data_objects import TrajectoryData
from .filter import Filter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthTimestepFilter(Filter):
    n: int

    def __init__(
        self,
        n: int,
    ):
        """
        This filter reduces the number
        of timesteps in simularium data

        Parameters
        ----------
        n : int
            keep every nth time step, filter out all the others
        """
        self.n = n

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Reduce the number of timesteps in each frame of the simularium
        data by filtering out all but every nth timestep
        """
        print(f"Filtering: every {self.n}th timestep -------------")
        if self.n < 2:
            raise Exception("N < 2: no timesteps will be filtered")
        # get filtered dimensions
        new_dimensions = DimensionData(
            total_steps=int(math.ceil(data.agent_data.times.size / float(self.n))),
            max_agents=int(np.amax(data.agent_data.n_agents)),
            max_subpoints=int(np.amax(data.agent_data.n_subpoints)),
        )
        result = AgentData.from_dimensions(new_dimensions)
        # get filtered data
        new_time_index = 0
        for time_index in range(data.agent_data.times.size):
            if time_index % self.n != 0:
                continue
            result.times[new_time_index] = data.agent_data.times[time_index]
            n_a = int(data.agent_data.n_agents[time_index])
            result.n_agents[new_time_index] = n_a
            for agent_index in range(n_a):
                result.viz_types[new_time_index][
                    agent_index
                ] = data.agent_data.viz_types[time_index][agent_index]
                result.unique_ids[new_time_index][
                    agent_index
                ] = data.agent_data.unique_ids[time_index][agent_index]
                result.types[new_time_index].append(
                    data.agent_data.types[time_index][agent_index]
                )
                result.positions[new_time_index][
                    agent_index
                ] = data.agent_data.positions[time_index][agent_index]
                result.radii[new_time_index][agent_index] = data.agent_data.radii[
                    time_index
                ][agent_index]
                result.rotations[new_time_index][
                    agent_index
                ] = data.agent_data.rotations[time_index][agent_index]
                result.n_subpoints[new_time_index][
                    agent_index
                ] = data.agent_data.n_subpoints[time_index][agent_index]
                result.subpoints[new_time_index][agent_index][
                    : np.shape(data.agent_data.subpoints[time_index][agent_index])[0]
                ] = data.agent_data.subpoints[time_index][agent_index]
            new_time_index += 1
        unique_types = set([tn for frame in result.types for tn in frame])
        for type_name in unique_types:
            if type_name in data.agent_data.display_data:
                result.display_data[type_name] = data.agent_data.display_data[type_name]
        data.agent_data = result
        print(
            f"filtered dims = {new_dimensions.total_steps} timesteps X "
            f"{new_dimensions.max_agents} agents X "
            f"{new_dimensions.max_subpoints} subpoints"
        )
        return data
