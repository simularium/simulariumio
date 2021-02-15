#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging

import numpy as np

from .filter import Filter
from .params import UpDirectionFilterParams, FilterParams
from ..data_objects import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class UpDirectionFilter(Filter):
    def _transform_position(
        self, position: np.ndarray, params: UpDirectionFilterParams
    ) -> np.ndarray:
        if params.up_dir == "Z":
            return np.array([position[0], -position[2], position[1]])
        else:
            return position

    def filter_spatial_data(
        self, agent_data: AgentData, params: UpDirectionFilterParams
    ) -> AgentData:
        """
        Reduce the number of subpoints in each frame of the simularium
        file by filtering out all but every nth subpoint
        """
        print("Filtering: up direction -------------")
        # get dimensions
        total_steps = agent_data.times.size
        max_agents = int(np.amax(agent_data.n_agents))
        max_subpoints = int(np.amax(agent_data.n_subpoints))
        # get filtered data
        positions = np.zeros((total_steps, max_agents, 3))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        for t in range(total_steps):
            for n in range(int(agent_data.n_agents[t])):
                positions[t][n] = self._transform_position(
                    agent_data.positions[t][n], params
                )
                if agent_data.n_subpoints[t][n] > 0:
                    for s in range(int(agent_data.n_subpoints[t][n])):
                        subpoints[t][n][s] = self._transform_position(
                            agent_data.subpoints[t][n][s], params
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
            draw_fiber_points=False,
            type_ids=agent_data.type_ids,
        )

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
