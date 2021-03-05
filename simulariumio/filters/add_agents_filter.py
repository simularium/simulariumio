#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging

import numpy as np

from ..data_objects import TrajectoryData, AgentData
from .filter import Filter
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AddAgentsFilter(Filter):
    new_agent_data: AgentData

    def __init__(self, new_agent_data: AgentData):
        """
        This filter adds the given agents
        to each frame of the simulation

        Parameters
        ----------
        new_agent_data : AgentData
            agent data to append to the trajectory
        """
        self.new_agent_data = new_agent_data

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Add the given agents to each frame of the simularium data
        """
        print("Filtering: add agents -------------")
        # get dimensions
        total_steps = data.agent_data.times.size
        new_total_steps = self.new_agent_data.times.size
        if new_total_steps != total_steps:
            raise DataError(
                "Timestep in data to add differs from existing: "
                f"new data has {new_total_steps} steps, while "
                f"existing data has {total_steps}"
            )
        max_agents = int(np.amax(data.agent_data.n_agents)) + int(
            np.amax(self.new_agent_data.n_agents)
        )
        max_subpoints = int(
            np.amax(data.agent_data.n_subpoints)
            if data.agent_data.n_subpoints is not None
            else 0
        ) + int(
            np.amax(self.new_agent_data.n_subpoints)
            if self.new_agent_data.n_subpoints is not None
            else 0
        )
        # get filtered data
        n_agents = np.zeros(total_steps)
        viz_types = np.zeros((total_steps, max_agents))
        unique_ids = np.zeros((total_steps, max_agents))
        used_uids = list(np.unique(data.agent_data.unique_ids))
        new_uids = {}
        types = []
        type_ids = np.zeros((total_steps, max_agents))
        if data.agent_data.type_ids is None:
            data.agent_data.type_ids, tm = AgentData.get_type_ids_and_mapping(
                data.agent_data.types
            )
        if self.new_agent_data.type_ids is None:
            self.new_agent_data.type_ids, tm = AgentData.get_type_ids_and_mapping(
                self.new_agent_data.types
            )
        positions = np.zeros((total_steps, max_agents, 3))
        radii = np.ones((total_steps, max_agents))
        n_subpoints = np.zeros((total_steps, max_agents))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        for t in range(total_steps):
            i = 0
            types.append([])
            n_a = int(data.agent_data.n_agents[t])
            for n in range(n_a):
                viz_types[t][i] = data.agent_data.viz_types[t][n]
                unique_ids[t][i] = data.agent_data.unique_ids[t][n]
                type_ids[t][i] = data.agent_data.type_ids[t][n]
                types[t].append(data.agent_data.types[t][n])
                positions[t][i] = data.agent_data.positions[t][n]
                radii[t][i] = data.agent_data.radii[t][n]
                if data.agent_data.n_subpoints is not None:
                    n_subpoints[t][i] = data.agent_data.n_subpoints[t][n]
                    subpoints[t][i][
                        : np.shape(data.agent_data.subpoints[t][n])[0]
                    ] = data.agent_data.subpoints[t][n]
                i += 1
            n_a = int(self.new_agent_data.n_agents[t])
            for n in range(n_a):
                viz_types[t][i] = self.new_agent_data.viz_types[t][n]
                raw_uid = self.new_agent_data.unique_ids[t][n]
                if raw_uid not in new_uids:
                    uid = raw_uid
                    while uid in used_uids:
                        uid += 1
                    new_uids[raw_uid] = uid
                    used_uids.append(uid)
                unique_ids[t][i] = new_uids[raw_uid]
                type_ids[t][i] = self.new_agent_data.type_ids[t][n]
                types[t].append(self.new_agent_data.types[t][n])
                positions[t][i] = self.new_agent_data.positions[t][n]
                radii[t][i] = self.new_agent_data.radii[t][n]
                if self.new_agent_data.n_subpoints is not None:
                    n_subpoints[t][i] = self.new_agent_data.n_subpoints[t][n]
                    subpoints[t][i][
                        : np.shape(self.new_agent_data.subpoints[t][n])[0]
                    ] = self.new_agent_data.subpoints[t][n]
                i += 1
            n_agents[t] = i
        return TrajectoryData(
            box_size=np.copy(data.box_size),
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
