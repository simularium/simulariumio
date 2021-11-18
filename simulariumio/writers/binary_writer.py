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
from ..constants import BINARY_SETTINGS, CURRENT_VERSION
from .writer import Writer
from .binary_chunk import BinaryChunk
from .binary_values import BinaryValues

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryWriter(Writer):
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
    def _format_trajectory_frame(
        global_time_index: int,
        chunk_time_index: int,
        agent_data: AgentData,
        type_ids: np.ndarray,
        buffer_size: int,
    ) -> List[BinaryValues]:
        """
        Return the frame of data as a list of BinaryValuess
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
            BinaryValues(
                values=[bytes(BINARY_SETTINGS.EOF, "utf-8")],
                format_string=f"{len(BINARY_SETTINGS.EOF)}s",
            ),
        ]

    @staticmethod
    def format_trajectory_data(
        trajectory_data: TrajectoryData,
        max_frames: int = BINARY_SETTINGS.MAX_FRAMES,
        max_bytes: int = BINARY_SETTINGS.MAX_BYTES,
    ) -> Tuple[List[Dict[str, Any]], List[BinaryValues]]:
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
        # format data
        header = BINARY_SETTINGS.HEADER + "".join(
            str(i) for i in BINARY_SETTINGS.VERSION
        )
        header_format = f"{len(header)}s"
        type_ids, type_mapping = trajectory_data.agent_data.get_type_ids_and_mapping()
        trajectory_infos = []
        binary_data = [[] for chunk in chunks]
        for chunk_index, chunk in enumerate(chunks):
            # trajectory info
            trajectory_infos.append(
                Writer._get_trajectory_info(
                    trajectory_data, chunk.n_frames, type_mapping
                )
            )
            # header
            binary_data[chunk_index].append(
                BinaryValues(
                    values=[bytes(header, "utf-8")],
                    format_string=header_format,
                )
            )
            # offset table
            binary_data[chunk_index].append(
                BinaryValues(
                    values=[chunk.n_frames] + chunk.frame_offsets,
                    format_string=f"{1 + len(chunk.frame_offsets)}i",
                )
            )
            # frame data
            for chunk_frame_index in range(chunk.n_frames):
                global_frame_index = chunk.get_global_index(chunk_frame_index)
                frame_data = BinaryWriter._format_trajectory_frame(
                    global_frame_index,
                    chunk_frame_index,
                    trajectory_data.agent_data,
                    type_ids,
                    frame_buffer_sizes[global_frame_index],
                )
                binary_data[chunk_index] += frame_data
        return trajectory_infos, binary_data

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
            trajectory_infos,
            binary_data,
        ) = BinaryWriter.format_trajectory_data(trajectory_data)
        print("Writing Binary -------------")
        for chunk_index in range(len(binary_data)):
            if len(binary_data) < 2:
                output_name = f"{output_path}.simularium"
            else:
                output_name = f"{output_path}_{chunk_index}.simularium"
            # trajectory info
            with open(output_name, "w") as outfile:
                json.dump(trajectory_infos[chunk_index], outfile)
            # spatial data
            format_string = "".join(
                value.format_string for value in binary_data[chunk_index]
            )
            data_buffer = [
                value
                for binary_values in binary_data[chunk_index]
                for value in binary_values.values
            ]
            with open(output_name, "ab") as outfile:
                outfile.write(struct.pack(format_string, *data_buffer))
            # plot data
            with open(output_name, "a") as outfile:
                json.dump(
                    {
                        "version": CURRENT_VERSION.PLOT_DATA,
                        "data": trajectory_data.plots,
                    },
                    outfile,
                )
            print(f"saved to {output_name}")
