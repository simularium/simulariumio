from typing import Dict, Union, Tuple


class DataIndices:
    def __init__(self, offset: int, length: int):
        """
        This object holds offset and length data for a binary
        simularium data block
        """
        self.offset = offset
        self.length = length

    def get_start_end_indices(self) -> Tuple[int, int]:
        """
        Return the start and end indicies for the data block
        """
        end = self.offset + self.length
        return self.offset, end


class FrameMetadata:
    def __init__(self, offset: int, length: int, frame_number: int, time: float):
        """
        This object holds metadata for a single frame of simularium data
        """
        self.offset = offset
        self.length = length
        self.frame_number = frame_number
        self.time = time

    def get_start_end_indices(self) -> Tuple[int, int]:
        """
        Return the start and end indicies for the frame
        """
        end = self.offset + self.length
        return self.offset, end


class FrameData:
    def __init__(
        self, frame_number: int, n_agents: int, time: float, data: Union[bytes, Dict]
    ):
        """
        This object holds frame data for a single frame of simularium data
        """
        self.frame_number = frame_number
        self.n_agents = n_agents
        self.time = time
        self.data = data
