#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

from ..data_objects import (
    AgentData,
    TrajectoryData,
)
from ..constants import BINARY_SETTINGS
from .writer import Writer
from .binary_chunk import BinaryChunk

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
            BINARY_SETTINGS.HEADER + "".join(str(i) for i in BINARY_SETTINGS.VERSION)
        )

    @staticmethod
    def _format_trajectory_frame(
        global_time_index: int,
        chunk_time_index: int,
        agent_data: AgentData,
        type_ids: np.ndarray,
        buffer_size: int,
    ) -> List[float]:
        """
        Return the frame of data as a bytes array
        """
        frame_buffer, _, _ = Writer._get_frame_buffer(
            global_time_index, agent_data, type_ids, buffer_size
        )
        return (
            [
                float(chunk_time_index),
                float(agent_data.times[global_time_index]),
                float(agent_data.n_agents[global_time_index]),
            ]
            + frame_buffer
            + BinaryWriter._str_to_float_array(BINARY_SETTINGS.EOF)
        )

    @staticmethod
    def _get_chunks(
        frame_buffer_sizes: List[int], max_frames: int, max_bytes: int
    ) -> List[BinaryChunk]:
        """
        Get number of frames, number of bytes, and number of values
        for each file that will be written,
        multiple files if needed to satisfy file size limits
        """
        n_constant_values = (
            len(BINARY_SETTINGS.HEADER) + len(BINARY_SETTINGS.VERSION) + 1
        )
        n_constant_bytes = n_constant_values + 3
        chunks = [BinaryChunk(0, n_constant_bytes, n_constant_values)]
        current_chunk = 0
        for frame_index, buffer_size in enumerate(frame_buffer_sizes):
            frame_bytes = 4 * (4 + buffer_size) + len(BINARY_SETTINGS.EOF)
            frame_values = 4 + buffer_size + len(BINARY_SETTINGS.EOF)
            if frame_bytes > max_bytes:
                raise Exception(
                    f"Frame {frame_index} is too large for a simularium file "
                    f"({frame_bytes} bytes), try filtering out some data."
                )
            if (
                chunks[current_chunk].n_frames >= max_frames
                or chunks[current_chunk].n_bytes + frame_bytes > max_bytes
            ):
                current_chunk += 1
                chunks.append(
                    BinaryChunk(0, n_constant_bytes, n_constant_values, frame_index)
                )
            chunks[current_chunk].n_frames += 1
            chunks[current_chunk].n_bytes += frame_bytes
            chunks[current_chunk].n_values += frame_values
        n_first_frame_offset = (
            len(BINARY_SETTINGS.HEADER) + len(BINARY_SETTINGS.VERSION) + 1
        )
        for chunk in chunks:
            data_index = n_first_frame_offset + chunk.n_frames
            for frame_index in range(chunk.n_frames):
                chunk.frame_offsets.append(data_index)
                data_index += (
                    3
                    + frame_buffer_sizes[chunk.get_global_index(frame_index)]
                    + len(BINARY_SETTINGS.EOF)
                )
        return chunks

    @staticmethod
    def format_trajectory_data(
        trajectory_data: TrajectoryData,
        max_frames: int = BINARY_SETTINGS.MAX_FRAMES,
        max_bytes: int = BINARY_SETTINGS.MAX_BYTES,
    ) -> List[np.ndarray]:
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
        frame_buffer_sizes = []
        for frame_index in range(total_steps):
            frame_buffer_sizes.append(
                Writer._get_frame_buffer_size(frame_index, trajectory_data.agent_data)
            )
        chunks = BinaryWriter._get_chunks(frame_buffer_sizes, max_frames, max_bytes)
        # get data
        result = [np.zeros(chunk.n_values, dtype="<f4") for chunk in chunks]
        header = BinaryWriter._header_to_float_array()
        type_ids, type_mapping = trajectory_data.agent_data.get_type_ids_and_mapping()
        for chunk_index, chunk in enumerate(chunks):
            result[chunk_index][: len(header)] = header[:]
            result[chunk_index][len(header)] = chunk.n_frames
            result[chunk_index][
                len(header) + 1 : len(header) + 1 + chunk.n_frames
            ] = chunk.frame_offsets[:]
            for chunk_frame_index in range(chunk.n_frames):
                global_frame_index = chunk.get_global_index(chunk_frame_index)
                result[chunk_index][
                    chunk.frame_offsets[chunk_frame_index] : chunk.frame_offsets[
                        chunk_frame_index
                    ]
                    + frame_buffer_sizes[global_frame_index]
                    + 3
                    + len(BINARY_SETTINGS.EOF)
                ] = BinaryWriter._format_trajectory_frame(
                    global_frame_index,
                    chunk_frame_index,
                    trajectory_data.agent_data,
                    type_ids,
                    frame_buffer_sizes[global_frame_index],
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
        data_buffers = BinaryWriter.format_trajectory_data(trajectory_data)
        print("Writing Binary -------------")
        for index, data_buffer in enumerate(data_buffers):
            data_buffer.astype("<f4").tofile(f"{output_path}_{index}.simularium")
            print(f"saved to {output_path}_{index}.simularium")
