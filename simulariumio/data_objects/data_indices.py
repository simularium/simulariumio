from typing import Tuple


class DataIndices:
    offset: int
    length: int

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
        end = self.offset + self.length - 1
        return self.offset, end
