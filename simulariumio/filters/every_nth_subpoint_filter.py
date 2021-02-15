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


class EveryNthSubpointFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: EveryNthAgentFilterParams
    ) -> AgentData:
        """
        Reduce the number of subpoints in each frame of the simularium
        file by filtering out all but every nth subpoint
        """
        print("Filtering: every Nth subpoint -------------")
        # get dimensions
        total_steps = agent_data.times.size
        max_agents = int(np.amax(agent_data.n_agents))
        max_subpoints = int(np.amax(agent_data.n_subpoints))
        # get filtered data
        n_subpoints = np.zeros((total_steps, max_agents))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        for t in range(total_steps):
            for n in range(int(agent_data.n_agents[t])):
                i = 0
                if agent_data.n_subpoints[t][n] > 0:
                    type_id = agent_data.type_ids[t][n]
                    if type_id in params.n_per_type_id:
                        inc = params.n_per_type_id[type_id]
                    else:
                        inc = params.default_n
                    for s in range(int(agent_data.n_subpoints[t][n])):
                        if s % inc != 0:
                            continue
                        subpoints[t][n][i] = agent_data.subpoints[t][n][s]
                        i += 1
                n_subpoints[t][n] = i
        return AgentData(
            times=agent_data.times,
            n_agents=agent_data.n_agents,
            viz_types=agent_data.viz_types,
            unique_ids=agent_data.unique_ids,
            types=agent_data.types,
            positions=agent_data.positions,
            radii=agent_data.radii,
            n_subpoints=n_subpoints,
            subpoints=subpoints,
            draw_fiber_points=False,
            type_ids=agent_data.type_ids,
        )

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
