#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, List, Tuple
import sys

import numpy as np

from .trajectory_reader import TrajectoryReader
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReaddyTrajectoryReader(TrajectoryReader):
    def _get_raw_trajectory_data(
        self, data: Dict[str, Any], scale_factor: float
    ) -> [Dict[str, Any], Any]:
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
            for i in range(agent_data["n_agents"][t]):
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
            for i in range(agent_data["n_agents"][t]):
                type_name = traj.species_name(agent_data["type_ids"][t][i])
                if (type_name in ignore_types or 
                    i >= n_filtered_particles_per_frame[t]):
                    continue
                result["unique_ids"][t][n] = agent_data["unique_ids"][t][i]
                result["type_ids"][t][n] = agent_data["type_ids"][t][i]
                result["positions"][t][n] = agent_data["positions"][t][i]
                result["radii"][t][n] = agent_data["radii"][t][i]
                n += 1
        return result

    def _group_particle_types(
        self, agent_data: Dict[str, Any], traj: Any, type_grouping: Dict[str, List[str]]
    ) -> Dict[str, Any]:
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
            for n in range(agent_data["n_agents"][t]):
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
        if "type_grouping" in data:
            agent_data = self._group_particle_types(agent_data, data["type_grouping"])   
        # shape data
        simularium_data = {}
        # trajectory info
        totalSteps = n_particles_per_frame.shape[0]
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": (
                float(data["timestep"]) else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": scale * float(data["box_size"][0]),
                "y": scale * float(data["box_size"][1]),
                "z": scale * float(data["box_size"][2]),
            },
            "typeMapping": {},
        }
        # add type names for each type that exists in the trajectory
        if len(type_names) > 0:
            existing_types = []
            for t in range(total_steps):
                for i in range(len(types[t])):
                    type_id = types[t][i]
                    if type_id not in existing_types:
                        existing_types.append(int(type_id))
            type_id_mapping = {}
            for type_id in existing_types:
                if type_id > len(type_names):
                    raise Exception(f"No type name provided for type ID {type_id}")
                traj_info["typeMapping"][str(type_id)] = {"name": type_names[type_id]}


        for tid in agent_types:
            s = str(tid)
            object_type = agent_types[tid]["object_type"]
            raw_id = str(agent_types[tid]["raw_id"])
            if (
                "agents" in data["data"][object_type]
                and raw_id in data["data"][object_type]["agents"]
                and "name" in data["data"][object_type]["agents"][raw_id]
            ):
                simularium_data["trajectoryInfo"]["typeMapping"][s] = {
                    "name": data["data"][object_type]["agents"][raw_id]["name"]
                }
            else:
                simularium_data["trajectoryInfo"]["typeMapping"][s] = {
                    "name": object_type[:-1] + raw_id
                }
        # spatial data
        draw_fiber_points = (
            bool(data["data"]["fibers"]["draw_points"])
            if "fibers" in data["data"] and "draw_points" in data["data"]["fibers"]
            else False
        )
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
