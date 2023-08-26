from typing import Tuple


class FrameMetadata:
    offset: int
    length: int
    frame_number: int
    time: float

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
        end = self.offset + self.length - 1
        return self.offset, end
