#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, List, Tuple

import numpy as np
import readdy

from .trajectory_reader import TrajectoryReader
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReaddyTrajectoryReader(TrajectoryReader):
    def _get_raw_trajectory_data(
        self, data: Dict[str, Any], scale_factor: float
    ) -> Tuple[Dict[str, Any], Any]:
        '''
        Return agent data populated from a ReaDDy .h5 trajectory file
        '''
        # load the trajectory
        traj = readdy.Trajectory(data["path_to_readdy_h5"])
        n_particles_per_frame, positions, types, ids = traj.to_numpy(start=0, stop=None)
        totalSteps = n_particles_per_frame.shape[0]
        max_n_particles = int(np.amax(n_particles_per_frame))
        result = {
            "times" : float(data["timestep"]) * np.arange(totalSteps),
            "n_agents" : n_particles_per_frame,
            "viz_types" : 1000.0 * np.ones(shape=(totalSteps, max_n_particles)),
            "unique_ids" : ids,
            "type_ids" : types,
            "positions" : scale_factor * positions,
            "radii" : np.ones(shape=(totalSteps, max_n_particles)),
        }
        # optionally set radius by particle type
        if "radii" in data:
            for t in range(len(n_particles_per_frame)):
                for n in range(n_particles_per_frame[t]):
                    type_name = traj.species_name(types[t][n])
                    if type_name in data["radii"]:
                        result["radii"][t][n] = float(data["radii"][type_name])
        return (result, traj)

    def _filter_trajectory_data(
        self, agent_data: Dict[str, Any], traj: Any, ignore_types: List[str]
    ) -> Dict[str, Any]:
        '''
        Remove particles with types to be ignored
        '''
        # get number of filtered particles
        totalSteps = len(agent_data["times"])
        n_filtered_particles_per_frame = np.zeros(totalSteps)
        for t in range(totalSteps):
            n = 0
            for i in range(int(agent_data["n_agents"][t])):
                if traj.species_name(agent_data["type_ids"][t][i]) not in ignore_types:
                    n += 1
            n_filtered_particles_per_frame[t] = n
        # filter particle data to remove ignored types
        max_n_particles = int(np.amax(n_filtered_particles_per_frame))
        result = {
            "times" : agent_data["times"],
            "viz_types" : agent_data["viz_types"],
            "n_agents" : n_filtered_particles_per_frame,
            "unique_ids" : -1 * np.ones((totalSteps, max_n_particles)),
            "type_ids" : np.zeros((totalSteps, max_n_particles)),
            "positions" : np.zeros((totalSteps, max_n_particles, 3)),
            "radii" : np.ones(shape=(totalSteps, max_n_particles)),
        }
        for t in range(len(agent_data["n_agents"])):
            n = 0
            for i in range(int(agent_data["n_agents"][t])):
                type_name = traj.species_name(agent_data["type_ids"][t][i])
                if (type_name in ignore_types or 
                    n >= n_filtered_particles_per_frame[t]):
                    continue
                result["unique_ids"][t][n] = agent_data["unique_ids"][t][i]
                result["type_ids"][t][n] = agent_data["type_ids"][t][i]
                result["positions"][t][n] = agent_data["positions"][t][i]
                result["radii"][t][n] = agent_data["radii"][t][i]
                n += 1
        return result

    def _group_particle_types(
        self, agent_data: Dict[str, Any], traj: Any, type_grouping: Dict[str, List[str]]
    ) -> Tuple[Dict[str, Any], Dict[str, Dict[str, str]]]:
        '''
        Group ReaDDy particle types by assigning them to new group type IDs
        '''
        # map ReaDDy ID to new group ID
        group_mapping = {}
        type_ids = traj.particle_types
        type_mapping = {}
        i = int(np.amax(agent_data["type_ids"])) + 1
        for group_type in type_grouping:
            type_mapping[str(i)] = {"name": group_type}
            for readdy_type in type_grouping[group_type]:
                group_mapping[type_ids[readdy_type]] = i
            i += 1
        # assign group ID to each particle of a type in the group
        for t in range(len(agent_data["n_agents"])):
            for n in range(int(agent_data["n_agents"][t])):
                readdy_id = agent_data["type_ids"][t][n]
                if readdy_id in group_mapping:
                    agent_data["type_ids"][t][n] = group_mapping[readdy_id]
        return (agent_data, type_mapping)

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        # load the data from a ReaDDy trajectory file
        scale = float(data["scale_factor"]) if "scale_factor" in data else 1.0
        agent_data, traj = self._get_raw_trajectory_data(data, scale)
        # optionally filter and group
        if "ignore_types" in data:
            agent_data = self._filter_trajectory_data(agent_data, traj, data["ignore_types"])
        type_mapping = {}
        if "type_grouping" in data:
            agent_data, type_mapping = self._group_particle_types(agent_data, traj, data["type_grouping"])
        # shape data
        simularium_data = {}
        # trajectory info
        totalSteps = agent_data["n_agents"].shape[0]
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": float(data["timestep"]),
            "totalSteps": totalSteps,
            "size": {
                "x": scale * float(data["box_size"][0]),
                "y": scale * float(data["box_size"][1]),
                "z": scale * float(data["box_size"][2]),
            },
            "typeMapping": type_mapping,
        }
        # add type names for each type that exists in the trajectory
        existing_type_ids = []
        for t in range(len(agent_data["n_agents"])):
            for n in range(int(agent_data["n_agents"][t])):
                type_id = int(agent_data["type_ids"][t][n])
                if type_id not in existing_type_ids:
                    existing_type_ids.append(type_id)
        for type_id in existing_type_ids:
            if str(type_id) not in simularium_data["trajectoryInfo"]["typeMapping"]:
                type_name = traj.species_name(type_id)
                simularium_data["trajectoryInfo"]["typeMapping"][str(type_id)] = {"name": type_name}
        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_no_subpoints(
                agent_data
            ),
        }
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": data["plots"] if "plots" in data else [],
        }
        return simularium_data
