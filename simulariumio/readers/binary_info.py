#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List
import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryFileData:
    byte_view: bytes
    int_view: np.ndarray
    float_view: np.ndarray


class BinaryBlockInfo:
    n_blocks: int
    block_offsets: List[int]
    block_types: List[int]
    block_lengths: List[int]

    def __init__(
        self,
        n_blocks: int,
        block_offsets: List[int],
        block_types: List[int],
        block_lengths: List[int],
    ):
        self.n_blocks = n_blocks
        self.block_offsets = block_offsets
        self.block_types = block_types
        self.block_lengths = block_lengths
