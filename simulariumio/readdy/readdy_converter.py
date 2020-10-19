#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import readdy

from ..converter import Converter
from ..data_objects import AgentData
from ..constants import VIZ_TYPE
from .readdy_data import ReaddyData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReaddyConverter(Converter):
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
            viz_types=VIZ_TYPE.default * np.ones(shape=(totalSteps, max_agents)),
            unique_ids=ids,
            types=None,
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
            types=None,
            positions=np.zeros((totalSteps, max_agents, 3)),
            radii=np.ones(shape=(totalSteps, max_agents)),
        )
        result.type_ids = (np.zeros((totalSteps, max_agents)),)
        for t in range(agent_data.n_agents.shape[0]):
            n = 0
            for i in range(agent_data.n_agents[t].shape[1]):
                type_name = traj.species_name(agent_data.type_ids[t][i])
                if type_name in ignore_types or n >= n_filtered_particles_per_frame[t]:
                    continue
                result.unique_ids[t][n] = agent_data.unique_ids[t][i]
                result.type_ids[t][n] = agent_data.type_ids[t][i]
                result.positions[t][n] = agent_data.positions[t][i]
                result.radii[t][n] = agent_data.radii[t][i]
                n += 1
        return result

    def _group_particle_types(
        self, agent_data: AgentData, traj: Any, type_grouping: Dict[str, List[str]]
    ) -> Tuple[AgentData, Dict[str, Dict[str, str]]]:
        """
        Group ReaDDy particle types by assigning them to new group type IDs
        """
        # map ReaDDy ID to new group ID
        group_mapping = {}
        type_map = traj.particle_types
        type_mapping = {}
        i = int(np.amax(agent_data.type_ids)) + 1
        for group_type in type_grouping:
            type_mapping[str(i)] = {"name": group_type}
            for readdy_type in type_grouping[group_type]:
                if readdy_type in type_map:
                    group_mapping[type_map[readdy_type]] = i
                else:
                    log.warning(
                        f"type {readdy_type}, which was provided in the type_grouping, "
                        "doesn't exist in the ReaDDy model"
                    )
            i += 1
        # assign group ID to each particle of a type in the group
        for t in range(agent_data.n_agents.shape[0]):
            for n in range(agent_data.n_agents[t]):
                readdy_id = agent_data.type_ids[t][n]
                if readdy_id in group_mapping:
                    agent_data.type_ids[t][n] = group_mapping[readdy_id]
        return (agent_data, type_mapping)

    def _read(self, input_data: ReaddyData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        # load the data from a ReaDDy trajectory file
        agent_data, traj = self._get_raw_trajectory_data(input_data)
        # optionally filter and group
        if input_data.ignore_types is not None:
            agent_data = self._filter_trajectory_data(
                agent_data, traj, input_data.ignore_types
            )
        type_mapping = {}
        if input_data.type_grouping is not None:
            agent_data, type_mapping = self._group_particle_types(
                agent_data, traj, input_data.type_grouping
            )
        # shape data
        simularium_data = {}
        # trajectory info
        totalSteps = agent_data.n_agents.shape[0]
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": float(input_data.timestep),
            "totalSteps": totalSteps,
            "size": {
                "x": input_data.scale_factor * float(input_data.box_size[0]),
                "y": input_data.scale_factor * float(input_data.box_size[1]),
                "z": input_data.scale_factor * float(input_data.box_size[2]),
            },
            "typeMapping": type_mapping,
        }
        # add type names for each type that exists in the trajectory
        existing_type_ids = []
        for t in range(totalSteps):
            for n in range(int(agent_data.n_agents[t])):
                type_id = int(agent_data.type_ids[t][n])
                if type_id not in existing_type_ids:
                    existing_type_ids.append(type_id)
        for type_id in existing_type_ids:
            if str(type_id) not in simularium_data["trajectoryInfo"]["typeMapping"]:
                type_name = traj.species_name(type_id)
                simularium_data["trajectoryInfo"]["typeMapping"][str(type_id)] = {
                    "name": type_name
                }
        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_no_subpoints(agent_data),
        }
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": input_data.plots,
        }
        return simularium_data
