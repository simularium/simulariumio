#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class NeighborData:
    type_name_substrings: List[str]
    relative_position: np.ndarray
    neighbor_type_name_substrings: List[str]
    neighbor_relative_position: np.ndarray

    def __init__(
        self,
        type_name_substrings: List[str],
        relative_position: np.ndarray,
        neighbor_type_name_substrings: List[str] = None,
        neighbor_relative_position: np.ndarray = None,
    ):
        """
        This object stores relative neighbor particle positions needed
        to calculate a particle's orientation.

        Parameters
        ----------
        type_name_substrings: List[str]
            The substrings that must be found in the type name
            of this neighbor of the particle being oriented
        relative_position: np.ndarray
            The relative position
            of this neighbor of the particle being oriented
            in the space of the particle being oriented
        neighbor_type_name_substrings: List[str] (optional)
            The substrings that must be found in the type name
            of the neighbor of this neighbor of the particle being oriented
            Default: Don't calculate dependent particle orientations
                (e.g. particles with one neighbor at the end of a complex)
        neighbor_relative_position: np.ndarray (optional)
            The relative position of the neighbor
            of this neighbor of the particle being oriented
            in the space of the particle being oriented
            Default: Don't calculate dependent particle orientations
                (e.g. particles with one neighbor at the end of a complex)
        """
        self.type_name_substrings = type_name_substrings
        self.relative_position = relative_position
        self.neighbor_type_name_substrings = neighbor_type_name_substrings
        self.neighbor_relative_position = neighbor_relative_position
