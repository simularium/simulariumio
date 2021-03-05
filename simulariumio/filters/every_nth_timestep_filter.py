#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging
import math

import numpy as np

from ..data_objects import TrajectoryData, AgentData, MetaData
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
        max_subpoints = int(np.amax(data.agent_data.n_subpoints))
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
                n_subpoints[i][n] = data.agent_data.n_subpoints[t][n]
                subpoints[i][n][
                    : np.shape(data.agent_data.subpoints[t][n])[0]
                ] = data.agent_data.subpoints[t][n]
            i += 1
        return TrajectoryData(
            meta_data=MetaData(
                box_size=np.copy(data.meta_data.box_size),
                default_camera_position=np.copy(data.meta_data.default_camera_position),
                default_camera_rotation=np.copy(data.meta_data.default_camera_rotation),
            ),
            agent_data=AgentData(
                times=times,
                n_agents=n_agents,
                viz_types=viz_types,
                unique_ids=unique_ids,
                types=types,
                positions=positions,
                radii=radii,
                n_subpoints=n_subpoints,
                subpoints=subpoints,
                draw_fiber_points=data.agent_data.draw_fiber_points,
                type_ids=type_ids,
            ),
            time_units=copy.copy(data.time_units),
            spatial_units=copy.copy(data.spatial_units),
            plots=copy.copy(data.plots),
        )
