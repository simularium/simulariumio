#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import readdy

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData
from ..constants import VIZ_TYPE
from .readdy_data import ReaddyData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReaddyConverter(TrajectoryConverter):
    def __init__(self, input_data: ReaddyData):
        """
        This object reads simulation trajectory outputs
        from ReaDDy (https://readdy.github.io/)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : ReaddyData
            An object containing info for reading
            ReaDDy simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    def _get_raw_trajectory_data(self, input_data: ReaddyData) -> Tuple[AgentData, Any]:
        """
        Return agent data populated from a ReaDDy .h5 trajectory file
        """
        # load the trajectory
        traj = readdy.Trajectory(input_data.path_to_readdy_h5)
        n_particles_per_frame, positions, types, ids = traj.to_numpy(start=0, stop=None)
        totalSteps = n_particles_per_frame.shape[0]
        max_agents = int(np.amax(n_particles_per_frame))
        result = AgentData(
            times=input_data.timestep * np.arange(totalSteps),
            n_agents=n_particles_per_frame,
            viz_types=VIZ_TYPE.DEFAULT * np.ones(shape=(totalSteps, max_agents)),
            unique_ids=ids,
            types=[[] for t in range(totalSteps)],
            positions=input_data.scale_factor * positions,
            radii=np.ones(shape=(totalSteps, max_agents)),
        )
        result.type_ids = types
        # optionally set radius by particle type
        if input_data.radii is not None:
            type_map = traj.particle_types
            for type_name in input_data.radii:
                if type_name not in type_map:
                    log.warning(
                        f"type {type_name}, for which a radius was provided, "
                        "doesn't exist in the ReaDDy model so this "
                        "radius won't be used. "
                        "Please provide radii for the original ReaDDy type(s)."
                    )
            for t in range(totalSteps):
                for n in range(n_particles_per_frame[t]):
                    type_name = traj.species_name(types[t][n])
                    if type_name in input_data.radii:
                        result.radii[t][n] = input_data.radii[type_name]
        return (result, traj)

    def _filter_trajectory_data(
        self, agent_data: AgentData, traj: Any, ignore_types: List[str]
    ) -> AgentData:
        """
        Remove particles with types to be ignored
        """
        # check that the ignored types actually exist
        type_map = traj.particle_types
        atleast_one_type_to_ignore = False
        for type_name in ignore_types:
            if type_name not in type_map:
                log.warning(
                    f"type {type_name}, which was provided in ignore_types, "
                    "doesn't exist in the ReaDDy model so won't be ignored. "
                )
            else:
                atleast_one_type_to_ignore = True
        if not atleast_one_type_to_ignore:
            return agent_data
        # get number of filtered particles
        totalSteps = agent_data.times.size
        n_filtered_particles_per_frame = np.zeros(totalSteps)
        for t in range(totalSteps):
            n = 0
            for i in range(int(agent_data.n_agents[t])):
                if traj.species_name(agent_data.type_ids[t][i]) not in ignore_types:
                    n += 1
            n_filtered_particles_per_frame[t] = n
        # filter particle data to remove ignored types
        max_agents = int(np.amax(n_filtered_particles_per_frame))
        result = AgentData(
            times=agent_data.times,
            n_agents=n_filtered_particles_per_frame,
            viz_types=agent_data.viz_types,
            unique_ids=-1 * np.ones((totalSteps, max_agents)),
            types=[[] for t in range(totalSteps)],
            positions=np.zeros((totalSteps, max_agents, 3)),
            radii=np.ones(shape=(totalSteps, max_agents)),
        )
        result.type_ids = np.zeros((totalSteps, max_agents))
        for t in range(agent_data.n_agents.shape[0]):
            n = 0
            for i in range(agent_data.n_agents[t]):
                type_name = traj.species_name(agent_data.type_ids[t][i])
                if type_name in ignore_types or n >= n_filtered_particles_per_frame[t]:
                    continue
                result.unique_ids[t][n] = agent_data.unique_ids[t][i]
                result.type_ids[t][n] = agent_data.type_ids[t][i]
                result.positions[t][n] = agent_data.positions[t][i]
                result.radii[t][n] = agent_data.radii[t][i]
                n += 1
        return result

    def _set_particle_types(
        self, agent_data: AgentData, traj: Any, type_grouping: Dict[str, List[str]]
    ) -> AgentData:
        """
        Set particle type names and optionally group ReaDDy particle types
        by assigning them to new group type IDs
        """
        # warn user if a given type doesn't exist in ReaDDy
        readdy_type_map = traj.particle_types
        i = int(np.amax(agent_data.type_ids)) + 1
        if type_grouping is not None:
            for group_type_name in type_grouping:
                for readdy_type_name in type_grouping[group_type_name]:
                    if readdy_type_name not in readdy_type_map:
                        log.warning(
                            f"type {readdy_type_name}, which was provided "
                            "in the type_grouping, doesn't exist in the ReaDDy model"
                        )
        # map ReaDDy ID to new group ID if grouped
        group_mapping = {}
        group_id_mapping = {}
        group_name_mapping = {}
        type_mapping = {}
        for readdy_type_name in readdy_type_map:
            group = False
            if type_grouping is not None:
                for group_type_name in type_grouping:
                    if readdy_type_name in type_grouping[group_type_name]:
                        if group_type_name not in group_id_mapping:
                            group_id_mapping[group_type_name] = i
                            group_name_mapping[i] = group_type_name
                            i += 1
                        type_mapping[
                            float(group_id_mapping[group_type_name])
                        ] = group_type_name
                        group_mapping[
                            float(readdy_type_map[readdy_type_name])
                        ] = group_id_mapping[group_type_name]
                        group = True
                        break
            if not group:
                type_mapping[
                    float(readdy_type_map[readdy_type_name])
                ] = readdy_type_name
        # assign group ID to each particle of a type in the group, and assign type names
        for t in range(agent_data.n_agents.shape[0]):
            for n in range(int(agent_data.n_agents[t])):
                readdy_id = agent_data.type_ids[t][n]
                while n >= len(agent_data.types[t]):
                    agent_data.types[t].append("")
                if readdy_id in group_mapping:
                    group_id = group_mapping[readdy_id]
                    group_name = group_name_mapping[group_id]
                    agent_data.type_ids[t][n] = group_id
                    agent_data.types[t][n] = group_name
                else:
                    agent_data.types[t][n] = type_mapping[readdy_id]
        return agent_data

    def _read(self, input_data: ReaddyData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading ReaDDy Data -------------")
        agent_data, traj = self._get_raw_trajectory_data(input_data)
        # optionally filter and group
        if input_data.ignore_types is not None:
            agent_data = self._filter_trajectory_data(
                agent_data, traj, input_data.ignore_types
            )
        agent_data = self._set_particle_types(
            agent_data, traj, input_data.type_grouping
        )
        return TrajectoryData(
            box_size=input_data.scale_factor * input_data.box_size,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
