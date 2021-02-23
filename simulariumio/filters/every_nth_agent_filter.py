#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging

import numpy as np

from .filter import Filter
from .params import EveryNthAgentFilterParams, FilterParams
from ..data_objects import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthAgentFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: EveryNthAgentFilterParams
    ) -> AgentData:
        """
        Reduce the number of agents in each frame of the simularium
        file by filtering out all but every nth agent
        """
        print("Filtering: every Nth agent -------------")
        # get dimensions
        total_steps = agent_data.times.size
        max_agents = int(np.amax(agent_data.n_agents))
        max_subpoints = int(np.amax(agent_data.n_subpoints))
        # get filtered data
        n_agents = np.zeros(total_steps)
        viz_types = np.zeros((total_steps, max_agents))
        unique_ids = np.zeros((total_steps, max_agents))
        types = []
        type_ids = np.zeros((total_steps, max_agents))
        positions = np.zeros((total_steps, max_agents, 3))
        radii = np.ones((total_steps, max_agents))
        n_subpoints = np.zeros((total_steps, max_agents))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        for t in range(total_steps):
            i = 0
            types.append([])
            n_found = {}
            n_a = int(agent_data.n_agents[t])
            for n in range(n_a):
                type_id = int(agent_data.type_ids[t][n])
                if type_id not in n_found:
                    n_found[type_id] = -1
                n_found[type_id] += 1
                if type_id in params.n_per_type_id:
                    inc = params.n_per_type_id[type_id]
                else:
                    inc = params.default_n
                if inc < 1 or n_found[type_id] % inc != 0:
                    continue
                viz_types[t][i] = agent_data.viz_types[t][n]
                unique_ids[t][i] = agent_data.unique_ids[t][n]
                type_ids[t][i] = agent_data.type_ids[t][n]
                types[t].append(agent_data.types[t][n])
                positions[t][i] = agent_data.positions[t][n]
                radii[t][i] = agent_data.radii[t][n]
                n_subpoints[t][i] = agent_data.n_subpoints[t][n]
                subpoints[t][i][
                    : np.shape(agent_data.subpoints[t][n])[0]
                ] = agent_data.subpoints[t][n]
                i += 1
            n_agents[t] = i
        print(
            f"filtered dims = {total_steps} timesteps X "
            f"{int(np.amax(n_agents))} agents X {max_subpoints} subpoint"
        )
        return AgentData(
            times=agent_data.times,
            n_agents=n_agents,
            viz_types=viz_types,
            unique_ids=unique_ids,
            types=types,
            positions=positions,
            radii=radii,
            n_subpoints=n_subpoints,
            subpoints=subpoints,
            draw_fiber_points=False,
            type_ids=type_ids,
        )
