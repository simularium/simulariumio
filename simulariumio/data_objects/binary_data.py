from typing import Dict, List, Tuple
import numpy as np

from .frame_data import FrameData
from .input_file_data import InputFileData
from .trajectory_data import TrajectoryData
from .simularium_file_data import SimulariumFileData
from ..constants import BINARY_BLOCK_TYPE, BINARY_SETTINGS
from ..readers import BinaryBlockInfo, SimulariumBinaryReader


class BinaryData(SimulariumFileData):
    def __init__(self, file_contents: bytes):
        """
        This object holds binary encoded simulation trajectory file's
        data while staying close to the original file format

        Parameters
        ----------
        file_contents : bytes
            A byte array containing the data of an open .simularium file
        """
        self.file_contents = InputFileData(file_contents=file_contents)
        self.file_data = SimulariumBinaryReader._binary_data_from_source(
            self.file_contents
        )
        self.frame_metadata: List[FrameMetadata] = []
        self.block_info: BinaryBlockInfo = None
        # Maps block type id to block index
        self.block_indices: Dict[int, int] = {}
        self._parse_file()

    def _parse_file(self):
        # Read offset and length for each data block
        self.block_info = SimulariumBinaryReader._parse_binary_header(
            self.file_data.byte_view
        )
        for block_index in range(self.block_info.n_blocks):
            block_type_id = SimulariumBinaryReader._binary_block_type(
                block_index, self.block_info, self.file_data.int_view
            )
            self.block_indices[block_type_id] = block_index

        # Extract each frame's metadata
        spatial_block_index = self.block_indices[
            BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value
        ]
        block_offset = self.block_info.block_offsets[spatial_block_index]
        spatial_block_offset = (
            int(block_offset / BINARY_SETTINGS.BYTES_PER_VALUE)
            + BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
        )
        n_frames = self.file_data.int_view[spatial_block_offset + 1]
        current_frame_offset = (
            spatial_block_offset
            + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES
            + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_N_VALUES_PER_FRAME * n_frames
        )
        for i in range(n_frames):
            offset = (
                self.file_data.int_view[
                    spatial_block_offset
                    + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES
                    + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_N_VALUES_PER_FRAME * i
                ]
                + block_offset
            )
            length = self.file_data.int_view[
                spatial_block_offset
                + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES
                + BINARY_SETTINGS.SPATIAL_BLOCK_HEADER_N_VALUES_PER_FRAME * i
                + 1
            ]
            frame_number = self.file_data.int_view[current_frame_offset]
            time = self.file_data.float_view[current_frame_offset + 1]
            self.frame_metadata.append(
                FrameMetadata(offset, length, frame_number, time)
            )
            current_frame_offset += int(length / BINARY_SETTINGS.BYTES_PER_VALUE)

    def get_frame_at_index(self, frame_number: int) -> FrameData:
        """
        Return frame data for frame at index. If there is no frame at the index,
        return None.
        """
        if frame_number < 0 or frame_number >= len(self.frame_metadata):
            # invalid frame number requested
            return None

        metadata: FrameMetadata = self.frame_metadata[frame_number]
        start, end = metadata.get_start_end_indices()
        data = self.file_data.byte_view[start:end]
        return FrameData(
            frame_number=frame_number,
            n_agents=self.file_data.int_view[
                int(start / BINARY_SETTINGS.BYTES_PER_VALUE) + 2
            ],
            time=metadata.time,
            data=data,
        )

    def get_index_for_time(self, time: float) -> int:
        """
        Return index for frame closest to a given timestamp
        """
        closest_frame = -1
        min_dist = np.inf
        for frame in self.frame_metadata:
            dist = abs(frame.time - time)
            if dist < min_dist:
                min_dist = dist
                closest_frame = frame.frame_number
            else:
                # if dist is increasing, we've passed the closest frame
                break

        # frame index must be <= self.get_num_frames() - 1
        return min(closest_frame, self.get_num_frames() - 1)

    def get_trajectory_info(self) -> Dict:
        """
        Return trajectory info block for trajectory, as dict
        """
        block_index = self.block_indices[BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value]
        return SimulariumBinaryReader._binary_block_json(
            block_index, self.block_info, self.file_data.byte_view
        )

    def get_plot_data(self) -> Dict:
        """
        Return plot data block for trajectory, as dict
        """
        block_index = self.block_indices[BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value]
        return SimulariumBinaryReader._binary_block_json(
            block_index, self.block_info, self.file_data.byte_view
        )

    def get_trajectory_data_object(self) -> TrajectoryData:
        """
        Return the data of the trajectory, as a TrajectoryData object
        """
        trajectory_dict = SimulariumBinaryReader.load_binary(self.file_contents)
        return TrajectoryData.from_buffer_data(trajectory_dict)

    def get_file_contents(self) -> bytes:
        """
        Return raw file data, as bytes
        """
        return self.file_contents.get_contents()

    def get_num_frames(self) -> int:
        """
        Return number of frames in the trajectory
        """
        return len(self.frame_metadata)


class FrameMetadata:
    def __init__(self, offset: int, length: int, frame_number: int, time: float):
        """
        This object holds metadata for a single frame of simularium data

        Parameters
        ----------
        offset : int
            Number of bytes the block is offset from the start of the byte array
        length : int
            Number of bytes in the block
        frame_number : int
            Index of frame in the simulation
        time : float
            Elapsed simulation time of the frame
        """
        self.offset = offset
        self.length = length
        self.frame_number = frame_number
        self.time = time

    def get_start_end_indices(self) -> Tuple[int, int]:
        """
        Return the start and end indicies for the data block
        """
        end = self.offset + self.length
        return self.offset, end
