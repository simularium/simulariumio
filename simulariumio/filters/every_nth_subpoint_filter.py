#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData, AgentData, MetaData

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
        return TrajectoryData(
            meta_data=MetaData(
                box_size=np.copy(data.meta_data.box_size),
                default_camera_position=np.copy(data.meta_data.default_camera_position),
                default_camera_rotation=np.copy(data.meta_data.default_camera_rotation),
            ),
            agent_data=AgentData(
                times=np.copy(data.agent_data.times),
                n_agents=np.copy(data.agent_data.n_agents),
                viz_types=np.copy(data.agent_data.viz_types),
                unique_ids=np.copy(data.agent_data.unique_ids),
                types=copy.copy(data.agent_data.types),
                positions=np.copy(data.agent_data.positions),
                radii=np.copy(data.agent_data.radii),
                n_subpoints=n_subpoints,
                subpoints=subpoints,
                draw_fiber_points=data.agent_data.draw_fiber_points,
                type_ids=np.copy(data.agent_data.type_ids),
            ),
            time_units=copy.copy(data.time_units),
            spatial_units=copy.copy(data.spatial_units),
            plots=copy.copy(data.plots),
        )
