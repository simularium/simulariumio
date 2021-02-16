#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging

import numpy as np

from ..data_objects import AgentData
from .filter import Filter
from .params import ReorderAgentsFilterParams, FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReorderAgentsFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: ReorderAgentsFilterParams
    ) -> AgentData:
        """
        Change the type IDs of the agents, so that the agents are listed,
        and therefore colored, in a different order in the viewer
        """
        print("Filtering: reorder agents -------------")
        # get dimensions
        total_steps = agent_data.times.size
        max_agents = int(np.amax(agent_data.n_agents))
        # get filtered data
        type_ids = np.zeros((total_steps, max_agents))
        for t in range(agent_data.times.size):
            for n in range(int(agent_data.n_agents[t])):
                tid = agent_data.type_ids[t][n]
                if tid in params.type_id_mapping:
                    tid = params.type_id_mapping[tid]
                type_ids[t][n] = tid
        return AgentData(
            times=agent_data.times,
            n_agents=agent_data.n_agents,
            viz_types=agent_data.viz_types,
            unique_ids=agent_data.unique_ids,
            types=agent_data.types,
            positions=agent_data.positions,
            radii=agent_data.radii,
            n_subpoints=agent_data.n_subpoints,
            subpoints=agent_data.subpoints,
            draw_fiber_points=False,
            type_ids=type_ids,
        )

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
