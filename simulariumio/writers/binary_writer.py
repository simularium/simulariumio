#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple, Any, Dict
import struct
import json

import numpy as np

from ..data_objects import (
    AgentData,
    TrajectoryData,
)
from ..constants import BINARY_SETTINGS, BINARY_BLOCK_TYPE, CURRENT_VERSION
from .writer import Writer
from .binary_chunk import BinaryChunk
from .binary_values import BinaryValues

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryWriter(Writer):
    @staticmethod
    def _get_chunks(
        frame_buffer_sizes: List[int],
        max_bytes: int,
    ) -> List[BinaryChunk]:
        """
        Get number of frames, number of bytes, and number of values
        for each file that will be written,
        multiple files if needed to satisfy file size limits
        """
        n_constant_int_values = (
            BINARY_SETTINGS.N_HEADER_INT_VALUES()
            + BINARY_SETTINGS.BLOCK_HEADER_LENGTH * BINARY_SETTINGS.N_BLOCKS
        )
        n_constant_values = len(BINARY_SETTINGS.HEADER) + n_constant_int_values
        n_constant_bytes = (
            len(BINARY_SETTINGS.HEADER)
            + BINARY_SETTINGS.BYTES_PER_VALUE * n_constant_int_values
        )
        chunks = [BinaryChunk(0, n_constant_bytes, n_constant_values)]
        current_chunk = 0
        for frame_index, buffer_size in enumerate(frame_buffer_sizes):
            frame_values = BINARY_SETTINGS.FRAME_HEADER_LENGTH + buffer_size
            frame_bytes = BINARY_SETTINGS.BYTES_PER_VALUE * frame_values
            if frame_bytes > max_bytes:
                raise Exception(
                    f"Frame {frame_index} is too large for a simularium file "
                    f"({frame_bytes} bytes), try filtering out some data."
                )
            new_bytes = chunks[current_chunk].n_bytes - n_constant_bytes + frame_bytes
            if new_bytes > max_bytes:
                current_chunk += 1
                chunks.append(
                    BinaryChunk(0, n_constant_bytes, n_constant_values, frame_index)
                )
            chunks[current_chunk].n_frames += 1
            chunks[current_chunk].n_bytes += frame_bytes
            chunks[current_chunk].n_values += frame_values
        for chunk in chunks:
            data_index = 0
            for frame_index in range(chunk.n_frames):
                chunk.frame_offsets.append(data_index)
                data_index += (
                    BINARY_SETTINGS.FRAME_HEADER_LENGTH
                    + frame_buffer_sizes[chunk.get_global_index(frame_index)]
                )
        return chunks

    @staticmethod
    def _get_binary_header(
        chunk: BinaryChunk,
        header_length: int,
        traj_info_length: int,
        spatial_data_length: int,
        plot_data_length: int,
    ) -> BinaryValues:
        """
        Return the binary header values and format
        """
        header_format = (
            f"{len(BINARY_SETTINGS.HEADER)}s{BINARY_SETTINGS.N_HEADER_INT_VALUES()}i"
        )
        block_offsets = [
            0,
            traj_info_length,
            traj_info_length + spatial_data_length,
        ]
        block_offsets = [header_length + offset for offset in block_offsets]
        return BinaryValues(
            values=(
                [bytes(BINARY_SETTINGS.HEADER, "utf-8")]
                + [header_length, BINARY_SETTINGS.VERSION, BINARY_SETTINGS.N_BLOCKS]
                + block_offsets
                + BINARY_SETTINGS.DEFAULT_BLOCK_TYPES()
                + [traj_info_length, spatial_data_length, plot_data_length]
            ),
            format_string=header_format,
        )

    @staticmethod
    def _get_binary_spatial_data_header(
        chunk: BinaryChunk,
        constant_first_frame_offset: int,
        spatial_header_constant_size: int,
        spatial_data_length: int,
    ) -> BinaryValues:
        """
        Return spatial data header values and format
        """
        first_frame_offset = constant_first_frame_offset + chunk.n_frames
        chunk.frame_offsets = [
            offset + first_frame_offset for offset in chunk.frame_offsets
        ]
        return BinaryValues(
            values=(
                [BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY, spatial_data_length]
                + [CURRENT_VERSION.SPATIAL_DATA, chunk.n_frames]
                + chunk.frame_offsets
            ),
            format_string=f"{spatial_header_constant_size + len(chunk.frame_offsets)}i",
        )

    @staticmethod
    def _format_trajectory_frame(
        global_time_index: int,
        chunk_time_index: int,
        agent_data: AgentData,
        type_ids: np.ndarray,
        buffer_size: int,
    ) -> List[BinaryValues]:
        """
        Return the frame of data as a list of BinaryValues
        """
        frame_buffer, _, _ = Writer._get_frame_buffer(
            global_time_index, agent_data, type_ids, buffer_size
        )
        return [
            BinaryValues(
                values=[int(chunk_time_index)],
                format_string="i",
            ),
            BinaryValues(
                values=[float(agent_data.times[global_time_index])],
                format_string="f",
            ),
            BinaryValues(
                values=[int(agent_data.n_agents[global_time_index])],
                format_string="i",
            ),
            BinaryValues(
                values=frame_buffer,
                format_string=f"{len(frame_buffer)}f",
            ),
        ]

    @staticmethod
    def _get_binary_spatial_data(
        chunk: BinaryChunk,
        constant_first_frame_offset: int,
        spatial_header_constant_size: int,
        spatial_data_length: int,
        trajectory_data: TrajectoryData,
        type_ids: np.ndarray,
        frame_buffer_sizes: List[int],
    ) -> List[BinaryValues]:
        """
        Return spatial data block values and format
        """
        result = [
            BinaryWriter._get_binary_spatial_data_header(
                chunk,
                constant_first_frame_offset,
                spatial_header_constant_size,
                spatial_data_length,
            )
        ]
        for chunk_frame_index in range(chunk.n_frames):
            global_frame_index = chunk.get_global_index(chunk_frame_index)
            frame_data = BinaryWriter._format_trajectory_frame(
                global_frame_index,
                chunk_frame_index,
                trajectory_data.agent_data,
                type_ids,
                frame_buffer_sizes[global_frame_index],
            )
            result += frame_data
        return result

    @staticmethod
    def format_trajectory_data(
        trajectory_data: TrajectoryData,
        max_bytes: int = BINARY_SETTINGS.MAX_BYTES,
    ) -> Tuple[List[BinaryValues], List[Dict[str, Any]], List[BinaryValues], int, int]:
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
        # get a trajectory info to determine size
        type_ids, type_mapping = trajectory_data.agent_data.get_type_ids_and_mapping()
        traj_info = Writer._get_trajectory_info(
            trajectory_data, total_steps, type_mapping
        )
        traj_info_length = BINARY_SETTINGS.BLOCK_HEADER_LENGTH + len(
            json.dumps(traj_info)
        )
        # get plot data to determine size
        plot_data_length = BINARY_SETTINGS.BLOCK_HEADER_LENGTH + len(
            json.dumps(
                {
                    "version": CURRENT_VERSION.PLOT_DATA,
                    "data": trajectory_data.plots,
                },
            )
        )
        # determine how to chunk the data so the file sizes don't exceed max_bytes
        max_spatial_bytes = max_bytes - traj_info_length - plot_data_length
        chunks = BinaryWriter._get_chunks(frame_buffer_sizes, max_spatial_bytes)
        # format data
        header_length = (
            len(BINARY_SETTINGS.HEADER) + BINARY_SETTINGS.N_HEADER_INT_VALUES()
        )
        constant_first_frame_offset = (
            header_length
            + traj_info_length
            + BINARY_SETTINGS.BLOCK_HEADER_LENGTH
            + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_LENGTH
        )
        spatial_header_constant_size = (
            BINARY_SETTINGS.BLOCK_HEADER_LENGTH
            + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_LENGTH
        )
        n_constant_values = (
            header_length
            + BINARY_SETTINGS.BLOCK_HEADER_LENGTH * BINARY_SETTINGS.N_BLOCKS
        )
        binary_headers = [[] for chunk in chunks]
        trajectory_infos = []
        binary_spatial_data = [[] for chunk in chunks]
        for chunk_index, chunk in enumerate(chunks):
            # binary header
            spatial_data_length = (
                spatial_header_constant_size
                + chunk.n_frames
                + chunk.n_values
                - n_constant_values
            )
            binary_headers[chunk_index].append(
                BinaryWriter._get_binary_header(
                    chunk,
                    header_length,
                    traj_info_length,
                    spatial_data_length,
                    plot_data_length,
                )
            )
            # trajectory info
            trajectory_infos.append(
                Writer._get_trajectory_info(
                    trajectory_data, chunk.n_frames, type_mapping
                )
            )
            # spatial data
            binary_spatial_data[chunk_index] += BinaryWriter._get_binary_spatial_data(
                chunk,
                constant_first_frame_offset,
                spatial_header_constant_size,
                spatial_data_length,
                trajectory_data,
                type_ids,
                frame_buffer_sizes,
            )
        return (
            binary_headers,
            trajectory_infos,
            binary_spatial_data,
            traj_info_length,
            plot_data_length,
        )

    @staticmethod
    def _get_data_buffer_with_format(
        index: int, binary_data: List[BinaryValues]
    ) -> Tuple[List[float], str]:
        """
        Return the buffer of data at index and its format string
        """
        return (
            [
                value
                for binary_values in binary_data[index]
                for value in binary_values.values
            ],
            "".join(value.format_string for value in binary_data[index]),
        )

    @staticmethod
    def _save_to_file(
        data: List[Any],
        file_name: str,
        binary_format: str = "",
        append: bool = True,
        is_binary: bool = True,
    ) -> Tuple[List[float], str]:
        """
        Return the buffer of data at index and its format string
        """
        with open(
            file_name, ("a" if append else "w") + ("b" if is_binary else "")
        ) as outfile:
            if is_binary:
                outfile.write(struct.pack(binary_format, *data))
            else:
                json.dump(data, outfile)

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
        (
            binary_headers,
            trajectory_infos,
            binary_spatial_data,
            traj_info_length,
            plot_data_length,
        ) = BinaryWriter.format_trajectory_data(trajectory_data)
        traj_info_header_buffer = [BINARY_BLOCK_TYPE.TRAJ_INFO_JSON, traj_info_length]
        plot_data_header_buffer = [BINARY_BLOCK_TYPE.PLOT_DATA_JSON, plot_data_length]
        block_header_format = f"{BINARY_SETTINGS.BLOCK_HEADER_LENGTH}i"
        print("Writing Binary -------------")
        for chunk_index in range(len(binary_spatial_data)):
            # determine filename(s)
            if len(binary_headers) < 2:
                output_name = f"{output_path}.simularium"
            else:
                output_name = f"{output_path}_{chunk_index}.simularium"
            # binary header
            header_buffer, header_format = BinaryWriter._get_data_buffer_with_format(
                chunk_index, binary_headers
            )
            BinaryWriter._save_to_file(
                header_buffer,
                output_name,
                header_format,
                append=False,
                is_binary=True,
            )
            # trajectory info
            BinaryWriter._save_to_file(
                traj_info_header_buffer,
                output_name,
                block_header_format,
                is_binary=True,
            )
            BinaryWriter._save_to_file(
                trajectory_infos[chunk_index],
                output_name,
                is_binary=False,
            )
            # spatial data
            (
                spatial_data_buffer,
                spatial_format,
            ) = BinaryWriter._get_data_buffer_with_format(
                chunk_index, binary_spatial_data
            )
            BinaryWriter._save_to_file(
                spatial_data_buffer,
                output_name,
                spatial_format,
                is_binary=True,
            )
            # plot data
            BinaryWriter._save_to_file(
                plot_data_header_buffer,
                output_name,
                block_header_format,
                is_binary=True,
            )
            BinaryWriter._save_to_file(
                {
                    "version": CURRENT_VERSION.PLOT_DATA,
                    "data": trajectory_data.plots,
                },
                output_name,
                is_binary=False,
            )
            print(f"saved to {output_name}")
