from typing import Dict, List
import json
import numpy as np

from .data_indices import DataIndices
from .frame_data import FrameData
from .frame_metadata import FrameMetadata
from .input_file_data import InputFileData
from .trajectory_data import TrajectoryData
from .simularium_file_data import SimulariumFileData
from ..constants import BINARY_BLOCK_TYPE, BINARY_SETTINGS
from ..readers import BinaryBlockInfo, BinaryFileData, SimulariumBinaryReader


class BinaryData(SimulariumFileData):
    file_contents: InputFileData
    file_data: BinaryFileData
    file_name: str
    block_indices: Dict[int, DataIndices] = {}
    frame_metadata: List[FrameMetadata] = []

    def __init__(self, file_name: str, file_contents: bytes):
        """
        This object holds binary encoded simulation trajectory file's
        data while staying close to the original file format

        Parameters
        ----------
        file_name : str
            Name of the file
        file_contents : bytes
            A byte array containing the data of an open .simularium file
        """
        self.file_name = file_name
        self.file_contents = InputFileData(file_contents=file_contents)
        self.file_data = SimulariumBinaryReader._binary_data_from_source(
            self.file_contents
        )
        self._parse_file()

    def _parse_file(self):
        # Read offset / length for each data block
        block_info: BinaryBlockInfo = SimulariumBinaryReader._parse_binary_header(
            self.file_data.byte_view
        )
        for block_index in range(block_info.n_blocks):
            block_type_id = SimulariumBinaryReader._binary_block_type(
                block_index, block_info, self.file_data.int_view
            )
            self.block_indices[block_type_id] = DataIndices(
                offset=block_info.block_offsets[block_index],
                length=block_info.block_lengths[block_index],
            )

        # Extract each frame's metadata
        spatial_indices: DataIndices = self.block_indices[
            BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value
        ]
        spatial_block_offset = (
            int(spatial_indices.offset / BINARY_SETTINGS.BYTES_PER_VALUE)
            + BINARY_SETTINGS.BLOCK_HEADER_N_VALUES
        )
        n_frames = self.file_data.int_view[spatial_block_offset + 1]
        current_frame_offset = spatial_block_offset + 2 + 2 * n_frames
        for i in range(n_frames):
            offset = (
                self.file_data.int_view[spatial_block_offset + 2 + (2 * i)]
                + spatial_indices.offset
            )
            length = self.file_data.int_view[spatial_block_offset + 3 + 2 * i]
            frame_number = self.file_data.int_view[current_frame_offset]
            time = self.file_data.float_view[current_frame_offset + 1]
            self.frame_metadata.append(
                FrameMetadata(offset, length, frame_number, time)
            )
            current_frame_offset += int(length / BINARY_SETTINGS.BYTES_PER_VALUE)

    def get_frame_at_index(self, frame_number: int) -> FrameData:
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
        start, end = self.block_indices[
            BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value
        ].get_start_end_indices()
        start += BINARY_SETTINGS.BLOCK_HEADER_N_VALUES * BINARY_SETTINGS.BYTES_PER_VALUE
        traj_info_bytes = self.file_data.byte_view[start:end]
        return json.loads(traj_info_bytes.decode("utf-8").strip("\x00"))

    def get_plot_data(self) -> Dict:
        start, end = self.block_indices[
            BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value
        ].get_start_end_indices()
        start += BINARY_SETTINGS.BLOCK_HEADER_N_VALUES * BINARY_SETTINGS.BYTES_PER_VALUE
        traj_info_bytes = self.file_data.byte_view[start:end]
        return json.loads(traj_info_bytes.decode("utf-8").strip("\x00"))

    def get_trajectory_data_object(self) -> TrajectoryData:
        trajectory_dict = SimulariumBinaryReader.load_binary(self.file_contents)
        return TrajectoryData.from_buffer_data(trajectory_dict)

    def get_file_contents(self) -> bytes:
        return self.file_contents.get_contents()

    def get_num_frames(self) -> int:
        return len(self.frame_metadata)

    def get_file_name(self) -> str:
        return self.file_name
