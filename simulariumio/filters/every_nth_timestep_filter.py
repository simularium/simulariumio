#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math

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
        total_steps = int(math.ceil(data.agent_data.times.size / float(self.n)))
        max_agents = int(np.amax(data.agent_data.n_agents))
        max_subpoints = (
            int(np.amax(data.agent_data.n_subpoints))
            if data.agent_data.n_subpoints is not None
            else 0
        )
        # get filtered data
        times = np.zeros(total_steps)
        n_agents = np.zeros(total_steps)
        viz_types = np.zeros((total_steps, max_agents))
        unique_ids = np.zeros((total_steps, max_agents))
        types = []
        type_ids = np.zeros((total_steps, max_agents))
        positions = np.zeros((total_steps, max_agents, 3))
        radii = np.ones((total_steps, max_agents))
        n_subpoints = np.zeros((total_steps, max_agents))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        i = 0
        for t in range(data.agent_data.times.size):
            if t % self.n != 0:
                continue
            times[i] = data.agent_data.times[t]
            n_agents[i] = int(data.agent_data.n_agents[t])
            types.append([])
            for n in range(int(n_agents[i])):
                viz_types[i][n] = data.agent_data.viz_types[t][n]
                unique_ids[i][n] = data.agent_data.unique_ids[t][n]
                type_ids[i][n] = data.agent_data.type_ids[t][n]
                types[i].append(data.agent_data.types[t][n])
                positions[i][n] = data.agent_data.positions[t][n]
                radii[i][n] = data.agent_data.radii[t][n]
                if data.agent_data.n_subpoints is not None:
                    n_subpoints[i][n] = data.agent_data.n_subpoints[t][n]
                if data.agent_data.subpoints is not None:
                    subpoints[i][n][
                        : np.shape(data.agent_data.subpoints[t][n])[0]
                    ] = data.agent_data.subpoints[t][n]
            i += 1
        data.agent_data.times = times
        data.agent_data.n_agents = n_agents
        data.agent_data.viz_types = viz_types
        data.agent_data.unique_ids = unique_ids
        data.agent_data.types = types
        data.agent_data.type_ids = type_ids
        data.agent_data.positions = positions
        data.agent_data.radii = radii
        if data.agent_data.n_subpoints is not None:
            data.agent_data.n_subpoints = n_subpoints
        if data.agent_data.subpoints is not None:
            data.agent_data.subpoints = subpoints
        print(
            f"filtered dims = {times.shape[0]} timesteps X "
            f"{max_agents} agents X {max_subpoints} subpoints"
        )
        return data
