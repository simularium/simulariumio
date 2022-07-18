#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData
from .smoldyn_data import SmoldynData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SmoldynConverter(TrajectoryConverter):
    def __init__(self, input_data: SmoldynData):
        """
        This object reads simulation trajectory outputs
        from Smoldyn (http://www.smoldyn.org)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : SmoldynData
            An object containing info for reading
            Smoldyn simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    @staticmethod
    def _parse_dimensions(smoldyn_data_lines: List[str]) -> DimensionData:
        """
        Parse Smoldyn output files to get the number of timesteps
        and maximum agents per timestep
        """
        result = DimensionData(0, 0)
        agents = 0
        for line in smoldyn_data_lines:
            cols = line.split()
            if len(cols) == 2:
                if agents > result.max_agents:
                    result.max_agents = agents
                agents = 0
                result.total_steps += 1
            else:
                agents += 1
        if agents > result.max_agents:
            result.max_agents = agents
        return result

    @staticmethod
    def _parse_objects(
        smoldyn_data_lines: List[str],
        input_data: SmoldynData,
    ) -> AgentData:
        """
        Parse a Smoldyn output file to get AgentData
        """
        dimensions = SmoldynConverter._parse_dimensions(smoldyn_data_lines)
        result = AgentData.from_dimensions(dimensions)
        time_index = -1
        agent_index = 0
        for line in smoldyn_data_lines:
            if len(line) < 1:
                continue
            cols = line.split()
            if len(cols) == 2:
                if time_index >= 0:
                    result.n_agents[time_index] = agent_index
                agent_index = 0
                time_index += 1
                result.times[time_index] = float(cols[0])
            else:
                if len(cols) < 4:
                    raise Exception(
                        "Smoldyn data is not formatted as expected, "
                        "please use the Smoldyn `listmols` command for output"
                    )
                is_3D = len(cols) > 4
                result.unique_ids[time_index][agent_index] = int(
                    cols[4] if is_3D else cols[3]
                )
                raw_type_name = str(cols[0])
                result.types[time_index].append(
                    TrajectoryConverter._get_display_type_name_from_raw(
                        raw_type_name, input_data.display_data
                    )
                )
                result.positions[time_index][
                    agent_index
                ] = input_data.meta_data.scale_factor * np.array(
                    [
                        float(cols[1]),
                        float(cols[2]),
                        float(cols[3]) if is_3D else 0.0,
                    ]
                )
                result.radii[time_index][
                    agent_index
                ] = input_data.meta_data.scale_factor * (
                    input_data.display_data[raw_type_name].radius
                    if raw_type_name in input_data.display_data
                    and input_data.display_data[raw_type_name].radius is not None
                    else 1.0
                )
                agent_index += 1
        result.n_agents[time_index] = agent_index
        result.n_timesteps = time_index + 1
        return result

    @staticmethod
    def _read(input_data: SmoldynData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the Smoldyn data
        """
        print("Reading Smoldyn Data -------------")
        # load the data from Smoldyn output .txt file
        smoldyn_data = input_data.smoldyn_file.get_contents().split("\n")
        # parse
        agent_data = SmoldynConverter._parse_objects(smoldyn_data, input_data)
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
