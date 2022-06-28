#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryChunk:
    n_frames: int
    n_bytes: int
    n_values: int
    first_frame_index: int
    frame_n_values: List[int]

    def __init__(
        self,
        first_frame_index: int = 0,
    ):
        """
        Object to store size info for a binary file.
        BinaryChunk is used to determine how many files to save
        and how to chunk up the data,
        if the data is larger than the max file size.

        Parameters
        ----------
        first_frame_index: int (optional)
            Which time index does this chunk start at?
                Default: 0
        """
        self.first_frame_index = first_frame_index
        self.n_frames = 0
        self.n_bytes = 0
        self.n_values = 0
        self.frame_n_values = []

    def get_global_index(self, local_index: int) -> int:
        """
        Get the index in the entire trajectory for the index within this chunk

        Parameters
        ----------
        local_index: int
            The index of the frame within this chunk
        """
        return self.first_frame_index + local_index

    def __str__(self) -> str:
        return (
            f"BinaryChunk(frames={self.n_frames}, bytes={self.n_bytes}, "
            f"values={self.n_values}, starting at {self.first_frame_index}, "
            f"frame lengths={self.frame_n_values}"
        )
