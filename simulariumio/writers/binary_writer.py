#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

from ..data_objects import (
    AgentData,
    TrajectoryData,
)
from ..constants import BINARY_HEADER, BINARY_VERSION, BINARY_EOF
from .writer import Writer

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryWriter(Writer):
    @staticmethod
    def _str_to_float_array(data: str) -> List[float]:
        """
        Return the string as a float array
        """
        return [float(ord(i)) for i in data]

    @staticmethod
    def _header_to_float_array() -> List[float]:
        """
        Return the header and version as a float array
        """
        return BinaryWriter._str_to_float_array(
            BINARY_HEADER + "".join(str(i) for i in BINARY_VERSION)
        )

    @staticmethod
    def _format_trajectory_frame(
        time_index: int,
        agent_data: AgentData,
        type_ids: np.ndarray,
        buffer_sizes: List[int],
    ) -> List[float]:
        """
        Return the frame of data as a bytes array
        """
        frame_buffer, _, _ = Writer._get_frame_buffer(
            time_index, agent_data, type_ids, buffer_sizes[time_index]
        )
        return (
            [
                float(time_index),
                float(agent_data.times[time_index]),
                float(agent_data.n_agents[time_index]),
            ]
            + frame_buffer
            + BinaryWriter._str_to_float_array(BINARY_EOF)
        )

    @staticmethod
    def format_trajectory_data(trajectory_data: TrajectoryData) -> np.ndarray:
        """
        Return the data shaped for Simularium binary

        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to format
        """
        print("Converting Trajectory Data to Binary -------------")
        # get dimensions
        total_steps = (
            trajectory_data.agent_data.n_timesteps
            if trajectory_data.agent_data.n_timesteps >= 0
            else len(trajectory_data.agent_data.times)
        )
        offsets = []
        buffer_sizes = []
        data_index = len(BINARY_HEADER) + len(BINARY_VERSION) + 1 + total_steps
        for time_index in range(total_steps):
            offsets.append(data_index)
            buffer_size = Writer._get_frame_buffer_size(
                time_index, trajectory_data.agent_data
            )
            buffer_sizes.append(buffer_size)
            data_index += 3 + buffer_size + len(BINARY_EOF)
        # get data
        result = np.zeros(data_index, dtype="<f4")
        header = BinaryWriter._header_to_float_array()
        result[: len(header)] = header[:]
        result[len(header)] = float(total_steps)
        result[len(header) + 1 : len(header) + 1 + total_steps] = offsets[:]
        type_ids, type_mapping = trajectory_data.agent_data.get_type_ids_and_mapping()
        for time_index in range(total_steps):
            result[
                offsets[time_index] : offsets[time_index]
                + buffer_sizes[time_index]
                + 3
                + len(BINARY_EOF)
            ] = BinaryWriter._format_trajectory_frame(
                time_index, trajectory_data.agent_data, type_ids, buffer_sizes
            )
        return result

    @staticmethod
    def save(trajectory_data: TrajectoryData, output_path: str) -> None:
        """
        Save the simularium data in .simularium binary format
        at the output path

        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to save
        output_path: str
            where to save the file
        """
        data_buffer = BinaryWriter.format_trajectory_data(trajectory_data)
        print("Writing Binary -------------")
        data_buffer.astype("<f4").tofile(f"{output_path}.simularium")
        print(f"saved to {output_path}.simularium")
