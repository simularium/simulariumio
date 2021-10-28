#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData
from .vmd_data import VmdData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class VmdConverter(TrajectoryConverter):
    def __init__(self, input_data: VmdData):
        """
        This object reads simulation trajectory outputs
        from VMD (https://www.ks.uiuc.edu/Research/vmd/)
        and plot data and writes them in the format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : VmdData
            An object containing info for reading
            VMD simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    @staticmethod
    def _parse_dimensions(xyz_data_lines: List[str], ignore_types: List[str]) -> DimensionData:
        """
        Parse .xyz file to get the number of timesteps
        and maximum agents per timestep
        """
        result = DimensionData(0, 0)
        agents = 0
        for line in xyz_data_lines:
            if not line:
                continue
            cols = line.split()
            if cols[0] == "1363":
                if agents > result.max_agents:
                    result.max_agents = agents
                agents = 0
                result.total_steps += 1
            elif len(cols) == 4:
                raw_type_name = str(cols[0])
                if raw_type_name in ignore_types:
                    continue
                agents += 1
        result.total_steps += 1
        if agents > result.max_agents:
            result.max_agents = agents
        return result

    @staticmethod
    def _parse_xyz(
        xyz_data_lines: List[str],
        input_data: VmdData,
    ) -> AgentData:
        """
        Parse a VMD .xyz file to get AgentData
        """
        dimensions = VmdConverter._parse_dimensions(xyz_data_lines, input_data.ignore_types)
        result = AgentData.from_dimensions(dimensions)
        time_index = 0
        agent_index = 0
        for index, line in enumerate(xyz_data_lines):
            if not line:
                continue
            cols = line.split()
            if cols[0] == "1363":
                if index < 2:
                    continue
                if time_index >= 1:
                    result.n_agents[time_index] = agent_index
                agent_index = 0
                time_index += 1
                result.times[time_index] = time_index * input_data.timestep
            elif len(cols) == 4:
                raw_type_name = str(cols[0])
                if raw_type_name in input_data.ignore_types:
                    continue
                result.unique_ids[time_index][agent_index] = agent_index
                result.types[time_index].append(
                    input_data.display_data[raw_type_name].name
                    if raw_type_name in input_data.display_data
                    else raw_type_name
                )
                result.positions[time_index][agent_index] = (
                    input_data.meta_data.scale_factor * np.array(
                        [float(cols[1]), float(cols[2]), float(cols[3])]
                    )
                )
                result.radii[time_index][agent_index] = (
                    input_data.meta_data.scale_factor * (
                        input_data.display_data[raw_type_name].radius
                        if raw_type_name in input_data.display_data
                        and input_data.display_data[raw_type_name].radius is not None
                        else 1.0
                    )
                )
                agent_index += 1
        result.n_agents[time_index] = agent_index
        result.n_timesteps = time_index + 1
        return result

    @staticmethod
    def _read(input_data: VmdData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the VMD data
        """
        print("Reading VMD Data -------------")
        # load the data from VMD output .xyz file
        vmd_data = input_data.xyz_file.get_contents().split("\n")
        # parse
        agent_data = VmdConverter._parse_xyz(vmd_data, input_data)
        # get display data (geometry and color)
        for tid in input_data.display_data:
            display_data = input_data.display_data[tid]
            agent_data.display_data[display_data.name] = display_data
        # create TrajectoryData
        input_data.spatial_units.multiply(1.0 / input_data.meta_data.scale_factor)
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
