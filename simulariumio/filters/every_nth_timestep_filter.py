#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging
import math

import numpy as np

from ..data_objects import AgentData
from .filter import Filter
from .params import EveryNthTimestepFilterParams, FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthTimestepFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: EveryNthTimestepFilterParams
    ) -> AgentData:
        """
        Reduce the number of timesteps by filtering out
        all but every nth step
        """
        print(f"Filtering: every {params.n}th timestep -------------")
        if params.n < 2:
            raise Exception("N < 2: no timesteps will be filtered")
        # get filtered dimensions
        total_steps = int(math.ceil(agent_data.times.size / float(params.n)))
        max_agents = int(np.amax(agent_data.n_agents))
        max_subpoints = int(np.amax(agent_data.n_subpoints))
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
        for t in range(agent_data.times.size):
            if t % params.n != 0:
                continue
            times[i] = agent_data.times[t]
            n_agents[i] = int(agent_data.n_agents[t])
            types.append([])
            for n in range(int(n_agents[i])):
                viz_types[i][n] = agent_data.viz_types[t][n]
                unique_ids[i][n] = agent_data.unique_ids[t][n]
                type_ids[i][n] = agent_data.type_ids[t][n]
                types[i].append(agent_data.types[t][n])
                positions[i][n] = agent_data.positions[t][n]
                radii[i][n] = agent_data.radii[t][n]
                n_subpoints[i][n] = agent_data.n_subpoints[t][n]
                subpoints[i][n][
                    : np.shape(agent_data.subpoints[t][n])[0]
                ] = agent_data.subpoints[t][n]
            i += 1
        return AgentData(
            times=times,
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

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
