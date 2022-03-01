#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import struct
import logging
from typing import Any, Dict, Tuple

from .trajectory_converter import TrajectoryConverter
from .data_objects import TrajectoryData, UnitData, InputFileData
from .constants import CURRENT_VERSION, BINARY_SETTINGS
from .exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileConverter(TrajectoryConverter):
    def __init__(self, input_file: InputFileData):
        """
        This object loads data from the input file in .simularium format.

        Parameters
        ----------
        input_file: InputFileData
            A InputFileData object containing .simularium data to load
        """
        try:
            print("Reading Simularium JSON -------------")
            buffer_data = json.loads(input_file.get_contents())
        except UnicodeDecodeError:
            print("Reading Simularium binary -------------")
            buffer_data = FileConverter._load_binary(input_file)
        if (
            int(buffer_data["trajectoryInfo"]["version"])
            < CURRENT_VERSION.TRAJECTORY_INFO
        ):
            buffer_data = FileConverter.update_trajectory_info_version(buffer_data)
        self._data = TrajectoryData.from_buffer_data(buffer_data)

    @staticmethod
    def _load_binary_int(
        open_binary_file: InputFileData, read_position: int
    ) -> Tuple[int, int]:
        """
        Load data from the input file in .simularium binary format and update it.
        """
        pos = read_position
        inc = BINARY_SETTINGS.BYTES_PER_VALUE
        result = int.from_bytes(
            open_binary_file.peek(pos + inc)[pos : pos + inc], byteorder="little"
        )
        return result, pos + inc

    @staticmethod
    def _load_binary(input_file: InputFileData) -> Dict[str, Any]:
        """
        Load data from the input file in .simularium binary format and update it.
        """
        block_header_length = (
            BINARY_SETTINGS.BYTES_PER_VALUE * BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
        )
        result = {}
        with open(input_file.file_path, "rb") as myfile:
            # parse header
            pos = len(BINARY_SETTINGS.HEADER)
            binary_id = myfile.peek(pos)[:pos].decode("utf-8")
            if binary_id != BINARY_SETTINGS.HEADER:
                raise DataError("Binary file is not in .simularium format")
            header_length, pos = FileConverter._load_binary_int(myfile, pos)
            index = 0
            header_values = []
            while pos < header_length:
                value, pos = FileConverter._load_binary_int(myfile, pos)
                header_values.append(value)
            binary_version = header_values[0]
            if binary_version != BINARY_SETTINGS.VERSION:
                raise DataError(
                    "Binary parsing only implemented for "
                    f"version >= 2, found {binary_version}"
                )
            n_blocks = header_values[1]
            block_offsets = header_values[2::3]
            block_types = header_values[3::3]
            block_lengths = header_values[4::3]
            # parse blocks
            for block_index in range(n_blocks):
                pos = block_offsets[block_index]
                # block header
                block_type, pos = FileConverter._load_binary_int(myfile, pos)
                if block_type != block_types[block_index]:
                    raise DataError(
                        "Block type is not consistent for block "
                        f"{block_index}: {block_type} != {block_types[block_index]}"
                    )
                block_length, pos = FileConverter._load_binary_int(myfile, pos)
                if block_length != block_lengths[block_index]:
                    raise DataError(
                        "Block length is not consistent for block "
                        f"{block_index}: {block_length} != {block_lengths[block_index]}"
                    )
                if block_type == 0:
                    # spatial data in JSON, this should never happen in a binary file
                    raise DataError(
                        "Reading spatial data as JSON from "
                        "binary files is not implemented"
                    )
                elif block_type == 1:
                    # trajectory info in JSON
                    result["trajectoryInfo"] = json.loads(
                        myfile.peek(pos + block_length - block_header_length)[
                            pos : pos + block_length - block_header_length
                        ]
                        .decode("utf-8")
                        .strip("\x00")
                    )
                    pos += block_length - block_header_length
                elif block_type == 2:
                    # plot data in JSON
                    result["plotData"] = json.loads(
                        myfile.peek(pos + block_length - block_header_length)[
                            pos : pos + block_length - block_header_length
                        ]
                        .decode("utf-8")
                        .strip("\x00")
                    )
                    pos += block_length - block_header_length
                elif block_type == 3:
                    # spatial data header
                    spatial_data_version, pos = FileConverter._load_binary_int(
                        myfile, pos
                    )
                    n_frames, pos = FileConverter._load_binary_int(myfile, pos)
                    spatial_block_header_length = BINARY_SETTINGS.BYTES_PER_VALUE * (
                        BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
                        + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES
                        + 2 * n_frames
                    )
                    frame_info = []
                    while (
                        pos < block_offsets[block_index] + spatial_block_header_length
                    ):
                        value, pos = FileConverter._load_binary_int(myfile, pos)
                        frame_info.append(value)
                    frame_lengths = frame_info[1::2]
                    result["spatialData"] = {
                        "version": spatial_data_version,
                        "msgType": 1,
                        "bundleStart": 0,
                        "bundleSize": n_frames,
                        "bundleData": [],
                    }
                    # parse frames
                    inc = BINARY_SETTINGS.BYTES_PER_VALUE
                    for index in range(n_frames):
                        # parse frame header
                        frame_index, pos = FileConverter._load_binary_int(myfile, pos)
                        if index == 0:
                            result["spatialData"]["bundleStart"] = frame_index
                        [timestamp] = struct.unpack(
                            "<f", myfile.peek(pos + inc)[pos : pos + inc]
                        )
                        pos += inc
                        n_agents, pos = FileConverter._load_binary_int(myfile, pos)
                        # parse frame data
                        frame_buffer_n_bytes = frame_lengths[index] - 3 * inc
                        frame_buffer_n_values = int(
                            frame_buffer_n_bytes / BINARY_SETTINGS.BYTES_PER_VALUE
                        )
                        frame_buffer = struct.unpack(
                            f"<{frame_buffer_n_values}f",
                            myfile.peek(pos + frame_buffer_n_bytes)[
                                pos : pos + frame_buffer_n_bytes
                            ],
                        )
                        result["spatialData"]["bundleData"].append(
                            {
                                "frameNumber": frame_index,
                                "time": timestamp,
                                "data": list(frame_buffer),
                            }
                        )
                        pos += frame_lengths[index] - 3 * inc
                else:
                    raise DataError(
                        f"Block type {block_types[block_index]} "
                        "is not a BINARY_BLOCK_TYPE"
                    )
        return result

    @staticmethod
    def _update_trajectory_info_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block from v1 to v2
        """
        # units
        if "spatialUnitFactorMeters" in data["trajectoryInfo"]:
            spatial_units = UnitData(
                "m", data["trajectoryInfo"]["spatialUnitFactorMeters"]
            )
            data["trajectoryInfo"].pop("spatialUnitFactorMeters")
        else:
            spatial_units = UnitData("m")
        data["trajectoryInfo"]["spatialUnits"] = {
            "magnitude": spatial_units.magnitude,
            "name": spatial_units.name,
        }
        time_units = UnitData("s", 1.0)
        data["trajectoryInfo"]["timeUnits"] = {
            "magnitude": time_units.magnitude,
            "name": time_units.name,
        }
        data["trajectoryInfo"]["version"] = 2
        return data

    @staticmethod
    def _update_trajectory_info_v2_to_v3(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block from v2 to v3
        """
        # all the new fields from v2 to v3 are optional
        data["trajectoryInfo"]["version"] = 3
        return data

    @staticmethod
    def update_trajectory_info_version(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block
        to match the current version

        Parameters
        ----------
        data: Dict[str, Any]
            A .simularium JSON file loaded in memory as a Dict.
            This object will be mutated, not copied.
        """
        original_version = int(data["trajectoryInfo"]["version"])
        if original_version == 1:
            data = FileConverter._update_trajectory_info_v1_to_v2(data)
            data = FileConverter._update_trajectory_info_v2_to_v3(data)
        if original_version == 2:
            data = FileConverter._update_trajectory_info_v2_to_v3(data)
        print(
            f"Updated TrajectoryInfo v{original_version} -> "
            f"v{CURRENT_VERSION.TRAJECTORY_INFO}"
        )
        return data
