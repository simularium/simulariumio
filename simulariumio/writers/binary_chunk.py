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
    frame_offsets: List[int]

    def __init__(
        self,
        first_frame_index: int = 0,
        n_frames: int = 0,
        n_bytes: int = 0,
        n_values: int = 0,
        frame_offsets: List[int] = None,
    ):
        """
        Object to store size info for a binary file

        Parameters
        ----------
        first_frame_index: int (optional)
            Which time index does this chunk start at?
                Default: 0
        n_frames: int
            How many timesteps of data in this chunk?
                Default: 0, set later
        n_bytes: int
            How many bytes saved in this chunk?
                Default: 0, set later
        n_values: int
            How many values saved in this chunk?
                Default: 0, set later
        frame_offsets: List[int]
            A list of the local indices at which the frames in this chunk start
                Default: [], set later
        """
        self.n_frames = n_frames
        self.n_bytes = n_bytes
        self.n_values = n_values
        self.first_frame_index = first_frame_index
        self.frame_offsets = [] if frame_offsets is None else frame_offsets

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
            f"offsets={self.frame_offsets}"
        )
