#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Tuple

import numpy as np
import readdy

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData, DisplayData
from ..constants import DISPLAY_TYPE, VIZ_TYPE
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
        n_agents, positions, type_ids, ids = traj.to_numpy(start=0, stop=None)
        return (traj, n_agents, positions, type_ids, ids)

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
        for time_index in range(data_dimensions.total_steps):
            new_agent_index = 0
            for agent_index in range(int(n_agents[time_index])):
                tid = type_ids[time_index][agent_index]
                if traj.species_name(tid) in input_data.ignore_types:
                    continue
                raw_type_name = traj.species_name(tid)
                display_data = (
                    input_data.display_data[raw_type_name]
                    if raw_type_name in input_data.display_data
                    else DisplayData(
                        name=raw_type_name, display_type=DISPLAY_TYPE.SPHERE
                    )
                )
                result.unique_ids[time_index][new_agent_index] = ids[time_index][
                    agent_index
                ]
                result.types[time_index].append(display_data.name)
                result.display_data[display_data.name] = display_data
                result.positions[time_index][new_agent_index] = (
                    input_data.meta_data.scale_factor
                    * positions[time_index][agent_index]
                )
                result.radii[time_index][new_agent_index] = (
                    display_data.radius if display_data.radius is not None else 1.0
                )
                new_agent_index += 1
            result.n_agents[time_index] = new_agent_index
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
