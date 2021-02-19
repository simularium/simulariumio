#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging

import numpy as np

from .filter import Filter
from .params import TranslateFilterParams, FilterParams
from ..data_objects import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: TranslateFilterParams
    ) -> AgentData:
        """
        Add the XYZ translation to all spatial coordinates
        """
        print("Filtering: translation -------------")
        # get dimensions
        total_steps = agent_data.times.size
        max_agents = int(np.amax(agent_data.n_agents))
        max_subpoints = int(np.amax(agent_data.n_subpoints))
        # get filtered data
        positions = np.zeros((total_steps, max_agents, 3))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        # get filtered data
        for t in range(total_steps):
            for n in range(int(agent_data.n_agents[t])):
                if agent_data.type_ids[t][n] in params.translation_per_type_id:
                    translation = params.translation_per_type_id[
                        agent_data.type_ids[t][n]
                    ]
                else:
                    translation = params.default_translation
                n_subpoints = int(agent_data.n_subpoints[t][n])
                if n_subpoints > 0:
                    for s in range(int(agent_data.n_subpoints[t][n])):
                        for d in range(3):
                            subpoints[t][n][s][d] = (
                                agent_data.subpoints[t][n][s][d] + translation[d]
                            )
                else:
                    for d in range(3):
                        positions[t][n][d] = (
                            agent_data.positions[t][n][d] + translation[d]
                        )
        return AgentData(
            times=agent_data.times,
            n_agents=agent_data.n_agents,
            viz_types=agent_data.viz_types,
            unique_ids=agent_data.unique_ids,
            types=agent_data.types,
            positions=positions,
            radii=agent_data.radii,
            n_subpoints=agent_data.n_subpoints,
            subpoints=subpoints,
            draw_fiber_points=agent_data.draw_fiber_points,
            type_ids=agent_data.type_ids,
        )

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
