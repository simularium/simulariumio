#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryChunk:
    """
    Object to store size info for a binary file
    """

    n_frames: int
    n_bytes: int
    n_values: int
    first_frame_index: int
    frame_offsets: List[int]

    def __init__(
        self,
        _n_frames: int,
        _n_bytes: int,
        _n_values: int,
        _first_frame_index: int = 0,
        _frame_offsets: List[int] = None,
    ):
        self.n_frames = _n_frames
        self.n_bytes = _n_bytes
        self.n_values = _n_values
        self.first_frame_index = _first_frame_index
        self.frame_offsets = [] if _frame_offsets is None else _frame_offsets

    def get_global_index(self, local_index):
        """
        Get the index in the entire trajectory for the index within this chunk
        """
        return self.first_frame_index + local_index

    def to_string(self):
        return (
            f"BinaryChunk(frames={self.n_frames}, bytes={self.n_bytes}, "
            f"values={self.n_values}, starting at {self.first_frame_index}, "
            f"offsets={self.frame_offsets}"
        )