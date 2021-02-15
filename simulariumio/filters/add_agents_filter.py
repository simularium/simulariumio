#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging
import math

import numpy as np

from ..data_objects import AgentData
from .filter import Filter
from .params import AddAgentsFilterParams, FilterParams
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AddAgentsFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: AddAgentsFilterParams
    ) -> AgentData:
        """
        Add the given agents to each frame of the simulation
        """
        print(f"Filtering: add agents -------------")
        # get dimensions
        total_steps = agent_data.times.size
        new_total_steps = params.new_agent_data.times.size
        if new_total_steps != total_steps:
            raise DataError("Timestep in data to add differs from existing: "
                            f"new data has {new_total_steps} steps, while "
                            f"existing data has {total_steps}")
        max_agents = (int(np.amax(agent_data.n_agents)) + 
                      int(np.amax(params.new_agent_data.n_agents)))
        max_subpoints = (int(np.amax(agent_data.n_subpoints)) + 
                         int(np.amax(params.new_agent_data.n_subpoints)))
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
            n_a = int(agent_data.n_agents[t])
            for n in range(n_a):
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
            n_a = int(params.new_agent_data.n_agents[t])
            for n in range(n_a):
                viz_types[t][i] = params.new_agent_data.viz_types[t][n]
                unique_ids[t][i] = params.new_agent_data.unique_ids[t][n]
                type_ids[t][i] = params.new_agent_data.type_ids[t][n]
                types[t].append(params.new_agent_data.types[t][n])
                positions[t][i] = params.new_agent_data.positions[t][n]
                radii[t][i] = params.new_agent_data.radii[t][n]
                n_subpoints[t][i] = params.new_agent_data.n_subpoints[t][n]
                subpoints[t][i][
                    : np.shape(params.new_agent_data.subpoints[t][n])[0]
                ] = params.new_agent_data.subpoints[t][n]
                i += 1
            n_agents[t] = i
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

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
