#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import json
import logging
from typing import Any, Dict
import numpy as np

from ..data_objects import InputFileData
from ..constants import BINARY_SETTINGS, BINARY_BLOCK_TYPE
from ..exceptions import DataError
from .binary_info import BinaryFileData, BinaryBlockInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SimulariumBinaryReader:
    @staticmethod
    def _binary_data_from_source(input_file: InputFileData) -> BinaryFileData:
        """
        Read a .simularium binary file or take binary input bytes and return
        multiple views of the data
        """
        result = BinaryFileData()
        result.byte_view = input_file.get_contents()
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
        pos = (
            id_length
            + BINARY_SETTINGS.HEADER_CONSTANT_N_VALUES * BINARY_SETTINGS.BYTES_PER_VALUE
        )
        _, _, binary_version, n_blocks = struct.unpack(
            f"{id_length}sIII", data_as_bytes[:pos]
        )
        if binary_version != BINARY_SETTINGS.VERSION:
            raise DataError(
                "Binary file parsing only implemented for "
                f"version > 1 up to current version {BINARY_SETTINGS.VERSION}, "
                f"found {binary_version}"
            )
        block_info_length = (
            BINARY_SETTINGS.HEADER_N_VALUES_PER_BLOCK
            * BINARY_SETTINGS.BYTES_PER_VALUE
            * n_blocks
        )
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
    def load_binary(input_file: InputFileData) -> Dict[str, Any]:
        """
        Load data from the input file in .simularium binary format and update it.
        """
        result = {}
        binary_data = SimulariumBinaryReader._binary_data_from_source(input_file)
        block_info = SimulariumBinaryReader._parse_binary_header(binary_data.byte_view)
        # parse blocks
        found_blocks = []
        for block_index in range(block_info.n_blocks):
            block_type_id = SimulariumBinaryReader._binary_block_type(
                block_index, block_info, binary_data.int_view
            )
            if block_type_id == BINARY_BLOCK_TYPE.SPATIAL_DATA_JSON.value:
                block_type = "spatialData"
                data_type = "JSON"
            elif block_type_id == BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value:
                block_type = "trajectoryInfo"
                data_type = "JSON"
            elif block_type_id == BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value:
                block_type = "plotData"
                data_type = "JSON"
            elif block_type_id == BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value:
                block_type = "spatialData"
                data_type = "binary"
            else:
                print(f"Binary block type ID = {block_type_id} is not supported")
                continue
            if block_type in found_blocks:
                print(
                    f"WARNING: More than one {block_type} block found, "
                    "only using last one"
                )
            if data_type == "JSON":
                result[block_type] = SimulariumBinaryReader._binary_block_json(
                    block_index, block_info, binary_data.byte_view
                )
            elif block_type == "spatialData":
                result[block_type] = SimulariumBinaryReader._binary_block_spatial_data(
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
