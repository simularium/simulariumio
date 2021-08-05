#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData, UnitData, DimensionData
from .springsalad_data import SpringsaladData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SpringsaladConverter(TrajectoryConverter):
    def __init__(self, input_data: SpringsaladData):
        """
        This object reads simulation trajectory outputs
        from SpringSaLaD (https://vcell.org/ssalad)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : SpringsaladData
            An object containing info for reading
            SpringSaLaD simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    @staticmethod
    def _parse_dimensions(springsalad_data: List[str]) -> DimensionData:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get the number of timesteps
        and maximum agents per timestep
        """
        result = DimensionData(0, 0)
        agents = 0
        for line in springsalad_data:
            if "CurrentTime" in line:  # beginning of a frame
                if agents > result.max_agents:
                    result.max_agents = agents
                agents = 0
                result.total_steps += 1
            if "ID" in line:  # line has data for one agent
                agents += 1
        if agents > result.max_agents:
            result.max_agents = agents
        return result

    @staticmethod
    def _parse_springsalad_data(
        springsalad_data: List[str], input_data: SpringsaladData
    ) -> Tuple[AgentData, np.ndarray]:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get spatial data
        """
        dimensions = SpringsaladConverter._parse_dimensions(springsalad_data)
        result = AgentData.from_dimensions(dimensions)
        box_size = np.zeros(3)
        time_index = -1
        agent_index = 0
        for line in springsalad_data:
            cols = line.split()
            if "xsize" in line:
                box_size[0] = input_data.scale_factor * 2 * float(cols[1])
            if "ysize" in line:
                box_size[1] = input_data.scale_factor * 2 * float(cols[1])
            if "z_outside" in line:
                box_size[2] += input_data.scale_factor * 2 * float(cols[1])
            if "z_inside" in line:
                box_size[2] += input_data.scale_factor * 2 * float(cols[1])
            if "CurrentTime" in line:  # beginning of a scene
                agent_index = 0
                time_index += 1
                result.times[time_index] = float(
                    line.split("CurrentTime")[1].split()[0]
                )
            if "ID" in line:  # line has data for one agent in scene
                result.n_agents[time_index] += 1
                result.unique_ids[time_index][agent_index] = int(cols[1])
                type_name = cols[3]
                if type_name in input_data.display_names:
                    type_name = input_data.display_names[type_name]
                result.types[time_index].append(type_name)
                result.positions[time_index][
                    agent_index
                ] = input_data.scale_factor * np.array(
                    [float(cols[4]), float(cols[5]), float(cols[6])]
                )
                result.radii[time_index][agent_index] = input_data.scale_factor * float(
                    cols[2]
                )
                agent_index += 1
        result.n_timesteps = time_index + 1
        return result, box_size

    @staticmethod
    def _read(input_data: SpringsaladData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading SpringSaLaD Data -------------")
        with open(input_data.path_to_sim_view_txt, "r") as myfile:
            springsalad_data = myfile.read().split("\n")
        agent_data, box_size = SpringsaladConverter._parse_springsalad_data(
            springsalad_data, input_data
        )
        return TrajectoryData(
            meta_data=MetaData(
                box_size=box_size,
                camera_defaults=input_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("nm", 1.0 / input_data.scale_factor),
            plots=input_data.plots,
        )
