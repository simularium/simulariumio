#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple, Any, Dict, Union
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
    def _padding(n_bytes: int) -> int:
        """
        Return the number of bytes to pad, given the desired number.
        """
        remainder = n_bytes % BINARY_SETTINGS.BLOCK_OFFSET_BYTE_ALIGNMENT
        if remainder > 0:
            return BINARY_SETTINGS.BLOCK_OFFSET_BYTE_ALIGNMENT - remainder
        else:
            return 0

    @staticmethod
    def _frame_buffers_n_values(trajectory_data: TrajectoryData) -> List[int]:
        """
        Get the number of values in the bundle data buffer for each frame
        """
        total_steps = trajectory_data.agent_data.total_timesteps()
        result = []
        for frame_index in range(total_steps):
            result.append(
                Writer._get_frame_buffer_size(frame_index, trajectory_data.agent_data)
            )
        return result

    @staticmethod
    def _header_n_bytes() -> int:
        """
        Get length of binary header in bytes
        """
        return (
            len(BINARY_SETTINGS.FILE_IDENTIFIER)
            + BINARY_SETTINGS.BYTES_PER_VALUE * BINARY_SETTINGS.HEADER_N_INT_VALUES
        )

    @staticmethod
    def _trajectory_info_length(
        trajectory_data: TrajectoryData,
        type_mapping: Dict[str, Any],
    ) -> int:
        """
        Get length of trajectory info in JSON
        (n_bytes = n_values)
        """
        total_steps = trajectory_data.agent_data.total_timesteps()
        traj_info = Writer._get_trajectory_info(
            trajectory_data, total_steps, type_mapping
        )
        traj_info_n_bytes = (
            BINARY_SETTINGS.BLOCK_HEADER_N_VALUES * BINARY_SETTINGS.BYTES_PER_VALUE
            + len(json.dumps(traj_info))
        )
        return traj_info_n_bytes + BinaryWriter._padding(traj_info_n_bytes)

    @staticmethod
    def _plot_data_length(plots: List[Dict[str, Any]]) -> int:
        """
        Get length of plot data in JSON
        (n_bytes = n_values)
        """
        plot_data_n_bytes = (
            BINARY_SETTINGS.BLOCK_HEADER_N_VALUES * BINARY_SETTINGS.BYTES_PER_VALUE
            + len(
                json.dumps(
                    {
                        "version": CURRENT_VERSION.PLOT_DATA,
                        "data": plots,
                    },
                )
            )
        )
        return plot_data_n_bytes + BinaryWriter._padding(plot_data_n_bytes)

    @staticmethod
    def _chunk_files(
        trajectory_data: TrajectoryData,
        type_mapping: Dict[str, Any],
        frame_buffers_n_values: List[int],
        max_bytes: int,
    ) -> Tuple[List[BinaryChunk], int, int]:
        """
        Get number of frames, number of bytes, and number of values
        for each file that will be written,
        multiple files if needed to satisfy file size limits
        also return size of trajectory info and plot data
        """
        header_n_bytes = BinaryWriter._header_n_bytes()
        traj_info_n_bytes = BinaryWriter._trajectory_info_length(
            trajectory_data, type_mapping
        )
        plot_data_n_bytes = BinaryWriter._plot_data_length(trajectory_data.plots)
        max_spatial_bytes = (
            max_bytes - header_n_bytes - traj_info_n_bytes - plot_data_n_bytes
        )
        file_chunks = [BinaryChunk()]
        current_chunk = 0
        current_frames_bytes = 0
        for frame_index, buffer_size in enumerate(frame_buffers_n_values):
            spatial_header_n_values = (
                BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
                + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES
                + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_N_VALUES_PER_FRAME
                * (file_chunks[current_chunk].n_frames + 1)
            )
            spatial_header_n_bytes = (
                BINARY_SETTINGS.BYTES_PER_VALUE * spatial_header_n_values
            )
            frame_n_values = BINARY_SETTINGS.FRAME_HEADER_N_VALUES + buffer_size
            frame_n_bytes = BINARY_SETTINGS.BYTES_PER_VALUE * frame_n_values
            if frame_n_bytes > max_spatial_bytes:
                raise Exception(
                    f"Frame {frame_index} is too large for a simularium file "
                    f"({frame_n_bytes} bytes), try filtering out some data."
                )
            new_bytes = spatial_header_n_bytes + current_frames_bytes + frame_n_bytes
            if new_bytes > max_spatial_bytes:
                file_chunks.append(BinaryChunk(frame_index))
                current_chunk += 1
                current_frames_bytes = 0
            file_chunks[current_chunk].n_frames += 1
            file_chunks[current_chunk].n_values += frame_n_values
            file_chunks[current_chunk].frame_n_values.append(frame_n_values)
            current_frames_bytes += frame_n_bytes
        for chunk in file_chunks:
            chunk.n_bytes = BINARY_SETTINGS.BYTES_PER_VALUE * (
                BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
                + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES
                + 2 * chunk.n_frames  # frame offsets and lengths
                + chunk.n_values
            )
        return file_chunks, traj_info_n_bytes, plot_data_n_bytes

    @staticmethod
    def _binary_header(
        traj_info_n_bytes: int,
        spatial_data_n_bytes: int,
        plot_data_n_bytes: int,
    ) -> BinaryValues:
        """
        Return the binary header values and format
        """
        header_n_bytes = BinaryWriter._header_n_bytes()
        header_format = (
            f"<{len(BINARY_SETTINGS.FILE_IDENTIFIER)}s"
            f"{BINARY_SETTINGS.HEADER_N_INT_VALUES}I"
        )
        block_types = BINARY_SETTINGS.DEFAULT_BLOCK_TYPES
        block_n_bytes = [traj_info_n_bytes, spatial_data_n_bytes, plot_data_n_bytes]
        block_offsets = [
            header_n_bytes,
            header_n_bytes + block_n_bytes[0],
            header_n_bytes + block_n_bytes[0] + block_n_bytes[1],
        ]
        return BinaryValues(
            values=(
                [bytes(BINARY_SETTINGS.FILE_IDENTIFIER, "utf-8")]
                + [header_n_bytes, BINARY_SETTINGS.VERSION, BINARY_SETTINGS.N_BLOCKS]
                + [
                    val
                    for tup in zip(block_offsets, block_types, block_n_bytes)
                    for val in tup
                ]
            ),
            format_string=header_format,
        )

    @staticmethod
    def _spatial_data_header(
        chunk: BinaryChunk,
    ) -> BinaryValues:
        """
        Return spatial data header values and format
        """
        n_header_values = (
            BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES + 2 * chunk.n_frames
        )  # frame offsets and lengths
        spatial_data_header_n_bytes = BINARY_SETTINGS.BYTES_PER_VALUE * n_header_values
        frame_offsets_and_lengths = []
        current_offset = (
            spatial_data_header_n_bytes
            + BINARY_SETTINGS.BYTES_PER_VALUE * BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
        )
        for frame_n_values in chunk.frame_n_values:
            frame_n_bytes = BINARY_SETTINGS.BYTES_PER_VALUE * frame_n_values
            frame_offsets_and_lengths.append(current_offset)
            frame_offsets_and_lengths.append(frame_n_bytes)
            current_offset += frame_n_bytes
        return BinaryValues(
            values=(
                [CURRENT_VERSION.SPATIAL_DATA, chunk.n_frames]
                + frame_offsets_and_lengths
            ),
            format_string=f"<{n_header_values}I",
        )

    @staticmethod
    def _formatted_frame(
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
                values=[
                    int(chunk_time_index),
                    float(agent_data.times[global_time_index]),
                    int(agent_data.n_agents[global_time_index]),
                ],
                format_string="IfI",
            ),
            BinaryValues(
                values=frame_buffer,
                format_string=f"{len(frame_buffer)}f",
            ),
        ]

    @staticmethod
    def _binary_spatial_data(
        chunk: BinaryChunk,
        trajectory_data: TrajectoryData,
        type_ids: np.ndarray,
        frame_buffers_n_values: List[int],
    ) -> List[BinaryValues]:
        """
        Return spatial data block values and format
        """
        result = [BinaryWriter._spatial_data_header(chunk)]
        for chunk_frame_index in range(chunk.n_frames):
            global_frame_index = chunk.get_global_index(chunk_frame_index)
            frame_data = BinaryWriter._formatted_frame(
                global_frame_index,
                chunk_frame_index,
                trajectory_data.agent_data,
                type_ids,
                frame_buffers_n_values[global_frame_index],
            )
            result += frame_data
        return result

    @staticmethod
    def format_trajectory_data(
        trajectory_data: TrajectoryData,
        max_bytes: int = BINARY_SETTINGS.MAX_BYTES,
    ) -> Tuple[List[BinaryValues], List[Dict[str, Any]], List[List[BinaryValues]]]:
        """
        Return the data shaped for Simularium binary
        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to format
        """
        print("Converting Trajectory Data to Binary -------------")
        trajectory_data.agent_data._check_subpoints_match_display_type()
        frame_buffers_n_values = BinaryWriter._frame_buffers_n_values(trajectory_data)
        type_ids, type_mapping = trajectory_data.agent_data.get_type_ids_and_mapping()
        file_chunks, traj_info_n_bytes, plot_data_n_bytes = BinaryWriter._chunk_files(
            trajectory_data, type_mapping, frame_buffers_n_values, max_bytes
        )
        # format data
        binary_headers = [[] for chunk in file_chunks]
        trajectory_infos = []
        binary_spatial_data = [[] for chunk in file_chunks]
        for chunk_index, file_chunk in enumerate(file_chunks):
            # binary header
            binary_headers[chunk_index].append(
                BinaryWriter._binary_header(
                    traj_info_n_bytes,
                    file_chunk.n_bytes,
                    plot_data_n_bytes,
                )
            )
            # trajectory info
            trajectory_infos.append(
                Writer._get_trajectory_info(
                    trajectory_data, file_chunk.n_frames, type_mapping
                )
            )
            # spatial data
            binary_spatial_data[chunk_index] += BinaryWriter._binary_spatial_data(
                file_chunk,
                trajectory_data,
                type_ids,
                frame_buffers_n_values,
            )
        return (
            binary_headers,
            trajectory_infos,
            binary_spatial_data,
        )

    @staticmethod
    def _data_buffer_with_format(
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
    def _write_block(
        data: Union[str, List[float]],
        block_type: int,
        file_name: str,
        binary_format: str = "",
        append: bool = True,
    ) -> int:
        """
        Write a binary block to a file
        Return number of bytes written
        """
        # pad to 4 byte boundary with zeros
        if isinstance(data, str):
            databytes = data.encode("utf-8")
            orig_len = len(databytes)
            padding = BinaryWriter._padding(orig_len)
            padformat = ""
            if padding > 0:
                padformat = f"{padding}x"
            databytes = struct.pack(f"{orig_len}s{padformat}", databytes)
        else:
            databytes = struct.pack(binary_format, *data)
        if len(databytes) % 4 != 0:
            raise ValueError("Binary data must be a multiple of 4 bytes")
        block_header_length = (
            BINARY_SETTINGS.BYTES_PER_VALUE * BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
        )
        mode = ("a" if append else "w") + "b"
        with open(file_name, mode) as outfile:
            # write block type
            outfile.write(struct.pack("<i", block_type))
            # write block size
            outfile.write(struct.pack("<i", len(databytes) + block_header_length))
            # write block data
            outfile.write(databytes)
        return len(databytes) + block_header_length

    @staticmethod
    def save(
        trajectory_data: TrajectoryData, output_path: str, validate_ids: bool
    ) -> None:
        """
        Save the simularium data in .simularium binary format
        at the output path
        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to save
        output_path: str
            where to save the file
        validate_ids: bool
            additional validation to check agent ID size?
        """
        if validate_ids:
            Writer._validate_ids(trajectory_data)
        (
            binary_headers,
            trajectory_infos,
            binary_spatial_data,
        ) = BinaryWriter.format_trajectory_data(trajectory_data)
        print("Writing Binary -------------")
        for chunk_index in range(len(binary_spatial_data)):
            # determine filename(s)
            if len(binary_headers) < 2:
                output_name = f"{output_path}.simularium"
            else:
                output_name = f"{output_path}_{chunk_index}.simularium"
            # binary header
            header_buffer, header_format = BinaryWriter._data_buffer_with_format(
                chunk_index, binary_headers
            )
            with open(output_name, "wb") as outfile:
                outfile.write(struct.pack(header_format, *header_buffer))
            # trajectory info
            BinaryWriter._write_block(
                json.dumps(trajectory_infos[chunk_index]),
                BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value,
                output_name,
            )
            # spatial data
            (
                spatial_data_buffer,
                spatial_format,
            ) = BinaryWriter._data_buffer_with_format(chunk_index, binary_spatial_data)
            BinaryWriter._write_block(
                spatial_data_buffer,
                BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value,
                output_name,
                spatial_format,
            )
            # plot data
            BinaryWriter._write_block(
                json.dumps(
                    {
                        "version": CURRENT_VERSION.PLOT_DATA,
                        "data": trajectory_data.plots,
                    }
                ),
                BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value,
                output_name,
            )
            print(f"saved to {output_name}")
