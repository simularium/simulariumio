#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Tuple, List, Dict

import numpy as np
import readdy

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData
from ..constants import VIZ_TYPE
from .readdy_data import ReaddyData
from ..orientations import ParticleRotationCalculator

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
    ) -> Tuple[Any, np.ndarray, np.ndarray, np.ndarray, np.ndarray, Any]:
        """
        Return agent data populated from a ReaDDy .h5 trajectory file
        """
        # load the trajectory
        traj = readdy.Trajectory(input_data.path_to_readdy_h5)
        n_agents, positions, type_ids, ids = traj.to_numpy(start=0, stop=None)
        try:
            _, topology_records = traj.read_observable_topologies()
        except ValueError:
            print(
                "Topologies were not observed so no orientations will be calculated. "
                "Use readdy.simulation.observe.topologies() "
                "before running the simulation to observe topologies."
            )
            topology_records = None
        return (traj, n_agents, positions, type_ids, ids, topology_records)

    @staticmethod
    def _get_edges_for_frame(
        time_index: int,
        topology_records: Any,
    ) -> Dict[int, List[int]]:
        """
        Get all the neighbors of each particle
        in each topology at the given time_index
        """
        if topology_records is None:
            return None
        result = {}
        for top in topology_records[time_index]:
            for e1, e2 in top.edges:
                if e1 > e2:
                    continue
                particle_id = int(top.particles[e1])
                if particle_id not in result:
                    result[particle_id] = []
                result[particle_id].append(int(top.particles[e2]))
        return result

    @staticmethod
    def _calculate_rotation(
        time_index: int,
        agent_index: int,
        edges: Dict[int, List[int]],
        traj: Any,
        positions: np.ndarray,
        type_ids: np.ndarray,
        ids: np.ndarray,
        agent_index_for_particle_id: List[Dict[int, int]],
        input_data: ReaddyData,
        rotations: np.ndarray,
        rotations_calculated: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate the rotation for a particle given
        its neighbors' positions and rotations
        """
        particle_id = ids[time_index][agent_index]
        particle_type_name = traj.species_name(type_ids[time_index][agent_index])
        particle_position = positions[time_index][agent_index]
        neighbor_type_names = []
        neighbor_positions = []
        neighbor_rotations = []
        for neighbor_id in edges[particle_id]:
            neighbor_index = agent_index_for_particle_id[time_index][neighbor_id]
            neighbor_type_names.append(
                traj.species_name(type_ids[time_index][neighbor_index])
            )
            neighbor_positions.append(positions[time_index][neighbor_index])
            if rotations is not None:
                neighbor_rotations.append(
                    rotations[time_index][neighbor_index]
                    if rotations_calculated[time_index][neighbor_index]
                    else None
                )
        return ParticleRotationCalculator.calculate_rotation(
            particle_type_name,
            particle_position,
            neighbor_type_names,
            neighbor_positions,
            neighbor_rotations if rotations is not None else None,
            input_data.zero_orientations,
            input_data.meta_data.box_size,
        )

    @staticmethod
    def _get_agent_data(
        input_data: ReaddyData,
    ) -> AgentData:
        """
        Pack raw ReaDDy trajectory data into AgentData,
        ignoring particles with type names in ignore_types
        """
        (
            traj,
            n_agents,
            positions,
            type_ids,
            ids,
            topology_records,
        ) = ReaddyConverter._get_raw_trajectory_data(input_data)
        data_dimensions = DimensionData(
            total_steps=n_agents.shape[0],
            max_agents=int(np.amax(n_agents)),
        )
        result = AgentData.from_dimensions(data_dimensions)
        result.times = input_data.timestep * np.arange(data_dimensions.total_steps)
        result.viz_types = VIZ_TYPE.DEFAULT * np.ones(
            shape=(data_dimensions.total_steps, data_dimensions.max_agents)
        )
        calculate_rotations = (
            input_data.zero_orientations is not None and topology_records is not None
        )
        rotations_calculated = np.zeros_like(result.rotations, dtype=bool)
        if calculate_rotations:
            agent_index_for_particle_id = []
            for time_index in range(len(topology_records)):
                agent_index_for_particle_id.append({})
                for agent_index, particle_id in enumerate(ids[time_index]):
                    agent_index_for_particle_id[time_index][particle_id] = agent_index
        for time_index in range(data_dimensions.total_steps):
            edges = ReaddyConverter._get_edges_for_frame(time_index, topology_records)
            new_agent_index = 0
            for agent_index in range(int(n_agents[time_index])):
                raw_type_name = traj.species_name(type_ids[time_index][agent_index])
                if raw_type_name in input_data.ignore_types:
                    continue
                display_data = (
                    input_data.display_data[raw_type_name]
                    if raw_type_name in input_data.display_data
                    else None
                )
                result.unique_ids[time_index][new_agent_index] = ids[time_index][
                    agent_index
                ]
                result.types[time_index].append(
                    display_data.name if display_data is not None else raw_type_name
                )
                result.positions[time_index][new_agent_index] = (
                    input_data.meta_data.scale_factor
                    * positions[time_index][agent_index]
                )
                result.radii[time_index][new_agent_index] = (
                    display_data.radius
                    if display_data is not None and display_data.radius is not None
                    else 1.0
                )
                if calculate_rotations:
                    rotation = ReaddyConverter._calculate_rotation(
                        time_index,
                        agent_index,
                        edges,
                        traj,
                        positions,
                        type_ids,
                        ids,
                        agent_index_for_particle_id,
                        input_data,
                        rotations=None,
                        rotations_calculated=None,
                    )
                    if rotation is not None:
                        rotations_calculated[time_index][new_agent_index] = True
                        result.rotations[time_index][new_agent_index] = rotation
                new_agent_index += 1
            result.n_agents[time_index] = new_agent_index
            if calculate_rotations:
                # calculate rotations that depend on neighbors' rotations
                for agent_index in range(int(n_agents[time_index])):
                    if rotations_calculated[time_index][agent_index]:
                        # this rotation was already set
                        continue
                    rotation = ReaddyConverter._calculate_rotation(
                        time_index,
                        agent_index,
                        edges,
                        traj,
                        positions,
                        type_ids,
                        ids,
                        agent_index_for_particle_id,
                        input_data,
                        result.rotations,
                        rotations_calculated,
                    )
                    if rotation is not None:
                        result.rotations[time_index][agent_index] = rotation
        return result

    @staticmethod
    def _read(input_data: ReaddyData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading ReaDDy Data -------------")
        agent_data = ReaddyConverter._get_agent_data(input_data)
        # get display data (geometry and color)
        for tid in input_data.display_data:
            display_data = input_data.display_data[tid]
            agent_data.display_data[display_data.name] = display_data
        input_data.spatial_units.multiply(1.0 / input_data.meta_data.scale_factor)
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
