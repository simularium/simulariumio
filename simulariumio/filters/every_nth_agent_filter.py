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


class EveryNthAgentFilter(Filter):
    n_per_type_id: Dict[int, int]
    default_n: int

    def __init__(self, n_per_type_id: Dict[int, int], default_n: int = 1):
        """
        This filter reduces the number of agents in each frame
        of simularium data by filtering out all but every nth agent

        Parameters
        ----------
        n_per_type_id : Dict[int, int]
            N for agents of each type ID,
            keep every nth agent of that type ID, filter out all the others
        default_n : int (optional)
            N for any agents of type not specified in n_per_type_id
            Default: 1
        """
        self.n_per_type_id = n_per_type_id
        self.default_n = default_n

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Reduce the number of agents in each frame of the simularium
        data by filtering out all but every nth agent
        """
        print("Filtering: every Nth agent -------------")
        # get filtered data
        total_steps = data.agent_data.times.size
        n_agents = np.zeros_like(data.agent_data.n_agents)
        viz_types = np.zeros_like(data.agent_data.viz_types)
        unique_ids = np.zeros_like(data.agent_data.unique_ids)
        types = []
        type_ids = np.zeros_like(data.agent_data.type_ids)
        positions = np.zeros_like(data.agent_data.positions)
        radii = np.ones_like(data.agent_data.radii)
        n_subpoints = np.zeros_like(data.agent_data.n_subpoints)
        subpoints = np.zeros_like(data.agent_data.subpoints)
        for t in range(total_steps):
            i = 0
            types.append([])
            n_found = {}
            n_a = int(data.agent_data.n_agents[t])
            for n in range(n_a):
                type_id = int(data.agent_data.type_ids[t][n])
                if type_id not in n_found:
                    n_found[type_id] = -1
                n_found[type_id] += 1
                if type_id in self.n_per_type_id:
                    inc = self.n_per_type_id[type_id]
                else:
                    inc = self.default_n
                if inc < 1 or n_found[type_id] % inc != 0:
                    continue
                viz_types[t][i] = data.agent_data.viz_types[t][n]
                unique_ids[t][i] = data.agent_data.unique_ids[t][n]
                type_ids[t][i] = data.agent_data.type_ids[t][n]
                types[t].append(data.agent_data.types[t][n])
                positions[t][i] = data.agent_data.positions[t][n]
                radii[t][i] = data.agent_data.radii[t][n]
                n_subpoints[t][i] = data.agent_data.n_subpoints[t][n]
                subpoints[t][i][
                    : np.shape(data.agent_data.subpoints[t][n])[0]
                ] = data.agent_data.subpoints[t][n]
                i += 1
            n_agents[t] = i
        max_subpoints = int(np.amax(data.agent_data.n_subpoints))
        print(
            f"filtered dims = {total_steps} timesteps X "
            f"{int(np.amax(n_agents))} agents X {max_subpoints} subpoint"
        )
        return TrajectoryData(
            meta_data=MetaData(
                box_size=np.copy(data.meta_data.box_size),
                default_camera_position=np.copy(data.meta_data.default_camera_position),
                default_camera_rotation=np.copy(data.meta_data.default_camera_rotation),
            ),
            agent_data=AgentData(
                times=np.copy(data.agent_data.times),
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
