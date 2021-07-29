#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import readdy

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData
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

    @staticmethod
    def _get_raw_trajectory_data(
        input_data: ReaddyData,
    ) -> Tuple[AgentData, Any, np.ndarray]:
        """
        Return agent data populated from a ReaDDy .h5 trajectory file
        """
        # load the trajectory
        traj = readdy.Trajectory(input_data.path_to_readdy_h5)
        n_particles_per_frame, positions, type_ids, ids = traj.to_numpy(
            start=0, stop=None
        )
        total_steps = n_particles_per_frame.shape[0]
        max_agents = int(np.amax(n_particles_per_frame))
        result = AgentData(
            times=input_data.timestep * np.arange(total_steps),
            n_agents=n_particles_per_frame,
            viz_types=VIZ_TYPE.DEFAULT * np.ones(shape=(total_steps, max_agents)),
            unique_ids=ids,
            types=[[] for t in range(total_steps)],
            positions=input_data.meta_data.scale_factor * positions,
            radii=np.ones(shape=(total_steps, max_agents)),
        )
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
            for time_index in range(total_steps):
                for agent_index in range(n_particles_per_frame[time_index]):
                    type_name = traj.species_name(type_ids[time_index][agent_index])
                    if type_name in input_data.radii:
                        result.radii[time_index][agent_index] = (
                            input_data.meta_data.scale_factor
                            * input_data.radii[type_name]
                        )
        result.n_timesteps = total_steps
        return (result, traj, type_ids)

    @staticmethod
    def _filter_trajectory_data(
        agent_data: AgentData,
        traj: Any,
        ignore_types: List[str],
        type_ids: np.ndarray,
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
        total_steps = agent_data.times.size
        n_filtered_particles_per_frame = np.zeros(total_steps)
        for time_index in range(total_steps):
            agent_index = 0
            for i in range(int(agent_data.n_agents[time_index])):
                if traj.species_name(type_ids[time_index][i]) not in ignore_types:
                    agent_index += 1
            n_filtered_particles_per_frame[time_index] = agent_index
        # filter particle data to remove ignored types
        max_agents = int(np.amax(n_filtered_particles_per_frame))
        result = AgentData(
            times=agent_data.times,
            n_agents=n_filtered_particles_per_frame,
            viz_types=agent_data.viz_types,
            unique_ids=-1 * np.ones((total_steps, max_agents)),
            types=[[] for t in range(total_steps)],
            positions=np.zeros((total_steps, max_agents, 3)),
            radii=np.ones(shape=(total_steps, max_agents)),
        )
        for time_index in range(agent_data.n_agents.shape[0]):
            for agent_index in range(agent_data.n_agents[time_index]):
                type_name = traj.species_name(type_ids[time_index][agent_index])
                if (
                    type_name in ignore_types
                    or agent_index >= n_filtered_particles_per_frame[time_index]
                ):
                    continue
                result.unique_ids[time_index][agent_index] = agent_data.unique_ids[
                    time_index
                ][agent_index]
                result.positions[time_index][agent_index] = agent_data.positions[
                    time_index
                ][agent_index]
                result.radii[time_index][agent_index] = agent_data.radii[time_index][
                    agent_index
                ]
        return result

    @staticmethod
    def _set_particle_types(
        agent_data: AgentData,
        traj: Any,
        type_grouping: Dict[str, List[str]],
        type_ids: np.ndarray,
    ) -> AgentData:
        """
        Set particle type names and optionally group ReaDDy particle types
        by assigning them to new group type IDs
        """
        # warn user if a given type doesn't exist in ReaDDy
        readdy_type_map = traj.particle_types
        i = int(np.amax(type_ids)) + 1
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
        for time_index in range(agent_data.n_agents.shape[0]):
            for agent_index in range(int(agent_data.n_agents[time_index])):
                readdy_id = type_ids[time_index][agent_index]
                if readdy_id in group_mapping:
                    group_id = group_mapping[readdy_id]
                    group_name = group_name_mapping[group_id]
                    agent_data.types[time_index].append(group_name)
                else:
                    agent_data.types[time_index].append(type_mapping[readdy_id])
        return agent_data

    @staticmethod
    def _read(input_data: ReaddyData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading ReaDDy Data -------------")
        agent_data, traj, type_ids = ReaddyConverter._get_raw_trajectory_data(
            input_data
        )
        # optionally filter and group
        if input_data.ignore_types is not None:
            agent_data = ReaddyConverter._filter_trajectory_data(
                agent_data, traj, input_data.ignore_types, type_ids
            )
        agent_data = ReaddyConverter._set_particle_types(
            agent_data, traj, input_data.type_grouping, type_ids
        )
        input_data.spatial_units.multiply(1.0 / input_data.meta_data.scale_factor)
        return TrajectoryData(
            meta_data=MetaData(
                box_size=input_data.meta_data.scale_factor
                * input_data.meta_data.box_size,
                camera_defaults=input_data.meta_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
