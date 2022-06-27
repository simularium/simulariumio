#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import json
import logging
from typing import Any, Dict
import numpy as np

from .trajectory_converter import TrajectoryConverter
from .data_objects import TrajectoryData, UnitData, InputFileData
from .constants import CURRENT_VERSION, BINARY_SETTINGS
from .exceptions import DataError
from .writers.binary_info import BinaryFileData, BinaryBlockInfo

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
        if input_file._is_binary_file():
            print("Reading Simularium binary -------------")
            buffer_data = FileConverter._load_binary(input_file)
        else:
            print("Reading Simularium JSON -------------")
            buffer_data = json.loads(input_file.get_contents())
        if (
            int(buffer_data["trajectoryInfo"]["version"])
            < CURRENT_VERSION.TRAJECTORY_INFO
        ):
            buffer_data = FileConverter.update_trajectory_info_version(buffer_data)
        self._data = TrajectoryData.from_buffer_data(buffer_data)

    @staticmethod
    def _binary_data_from_file(input_file: InputFileData) -> BinaryFileData:
        """
        Read a .simularium binary file and return multiple views of the data
        """
        result = BinaryFileData()
        with open(input_file.file_path, "rb") as open_binary_file:
            result.byte_view = open_binary_file.read()
            result.int_view = np.frombuffer(
                result.byte_view, dtype=np.dtype("I").newbyteorder("<")
            )
            result.float_view = np.frombuffer(
                result.byte_view, dtype=np.dtype("f").newbyteorder("<")
            )
        return result

    @staticmethod
    def _parse_binary_header(data_as_bytes: bytes) -> BinaryBlockInfo:
        """
        Parse header of data from a .simularium binary file
        """
        id_length = len(BINARY_SETTINGS.FILE_IDENTIFIER)
        pos = id_length + 3 * BINARY_SETTINGS.BYTES_PER_VALUE
        _, _, binary_version, n_blocks = struct.unpack(
            f"{id_length}sIII", data_as_bytes[:pos]
        )
        if binary_version != BINARY_SETTINGS.VERSION:
            raise DataError(
                "Binary file parsing only implemented for "
                f"version > 1 up to current version {BINARY_SETTINGS.VERSION}, "
                f"found {binary_version}"
            )
        block_info_length = 3 * BINARY_SETTINGS.BYTES_PER_VALUE * n_blocks
        block_info = struct.unpack(
            n_blocks * "III",
            data_as_bytes[pos : pos + block_info_length],
        )
        return BinaryBlockInfo(
            n_blocks=n_blocks,
            block_offsets=block_info[0::3],
            block_types=block_info[1::3],
            block_lengths=block_info[2::3],
        )

    @staticmethod
    def _binary_block_type(
        block_index: int,
        block_info: BinaryBlockInfo,
        data_as_ints: np.ndarray,
    ) -> int:
        """
        Parse block header of data from a .simularium binary file
        """
        block_offset = int(
            block_info.block_offsets[block_index] / BINARY_SETTINGS.BYTES_PER_VALUE
        )
        block_type = data_as_ints[block_offset]
        if block_type != block_info.block_types[block_index]:
            raise DataError(
                "Block type is not consistent for block "
                f"#{block_index} : {block_type} from block != "
                + block_info.block_types[block_index]
                + " from header"
            )
        block_length = data_as_ints[block_offset + 1]
        if block_length != block_info.block_lengths[block_index]:
            raise DataError(
                "Block length is not consistent for block "
                f"#{block_index} : {block_length} from block != "
                + block_info.block_lengths[block_index]
                + " from header"
            )
        return block_type

    @staticmethod
    def _binary_block_json(
        block_index: int,
        block_info: BinaryBlockInfo,
        data_as_bytes: bytes,
    ) -> Dict[str, Any]:
        """
        Parse JSON block from a .simularium binary file
        """
        block_offset = block_info.block_offsets[block_index]
        block_length = block_info.block_lengths[block_index]
        block_header_n_bytes = (
            BINARY_SETTINGS.BLOCK_HEADER_N_VALUES * BINARY_SETTINGS.BYTES_PER_VALUE
        )
        block_offset += block_header_n_bytes
        block_length -= block_header_n_bytes
        traj_info_bytes = data_as_bytes[block_offset : block_offset + block_length]
        return json.loads(traj_info_bytes.decode("utf-8").strip("\x00"))

    @staticmethod
    def _binary_block_spatial_data(
        block_index: int,
        block_info: BinaryBlockInfo,
        data_as_ints: np.ndarray,
        data_as_floats: np.ndarray,
    ) -> Dict[str, Any]:
        """
        Parse spatial data binary block from a .simularium binary file
        """
        block_offset = (
            int(block_info.block_offsets[block_index] / BINARY_SETTINGS.BYTES_PER_VALUE)
            + BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
        )
        spatial_data_version = data_as_ints[block_offset]
        n_frames = data_as_ints[block_offset + 1]
        current_frame_offset = block_offset + 2 + 2 * n_frames
        frame_info = data_as_ints[block_offset + 2 : current_frame_offset]
        frame_lengths = frame_info[1::2]
        result = {
            "version": spatial_data_version,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": n_frames,
            "bundleData": [],
        }
        for index in range(n_frames):
            frame_index = data_as_ints[current_frame_offset]
            if index == 0:
                result["bundleStart"] = frame_index
            frame_n_values = int(frame_lengths[index] / BINARY_SETTINGS.BYTES_PER_VALUE)
            result["bundleData"].append(
                {
                    "frameNumber": frame_index,
                    "time": data_as_floats[current_frame_offset + 1],
                    "data": list(
                        data_as_floats[
                            current_frame_offset
                            + 3 : current_frame_offset
                            + frame_n_values
                        ]
                    ),
                }
            )
            current_frame_offset += frame_n_values
        return result

    @staticmethod
    def _load_binary(input_file: InputFileData) -> Dict[str, Any]:
        """
        Load data from the input file in .simularium binary format and update it.
        """
        result = {}
        binary_data = FileConverter._binary_data_from_file(input_file)
        block_info = FileConverter._parse_binary_header(binary_data.byte_view)
        # parse blocks
        found_blocks = []
        for block_index in range(block_info.n_blocks):
            block_type_id = FileConverter._binary_block_type(
                block_index, block_info, binary_data.int_view
            )
            if block_type_id == 0:
                block_type = "spatialData"
                data_type = "JSON"
            elif block_type_id == 1:
                block_type = "trajectoryInfo"
                data_type = "JSON"
            elif block_type_id == 2:
                block_type = "plotData"
                data_type = "JSON"
            if block_type_id == 3:
                block_type = "spatialData"
                data_type = "binary"
            if block_type in found_blocks:
                print(
                    f"WARNING: More than one {block_type} block found, "
                    "only using last one"
                )
            if data_type == "JSON":
                result[block_type] = FileConverter._binary_block_json(
                    block_index, block_info, binary_data.byte_view
                )
            elif block_type == "spatialData":
                result["spatialData"] = FileConverter._binary_block_spatial_data(
                    block_index,
                    block_info,
                    binary_data.int_view,
                    binary_data.float_view,
                )
            else:
                raise DataError(
                    f"Binary {block_type} block reading is not yet supported"
                )
            found_blocks.append(block_type)
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
