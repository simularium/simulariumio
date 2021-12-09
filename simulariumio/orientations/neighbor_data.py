#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import logging
from typing import List

import numpy as np

from .rotation_utility import RotationUtility

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class NeighborData:
    type_name_substrings: List[str]
    relative_position: np.ndarray
    relative_rotation: np.ndarray
    neighbor_type_name_substrings: List[str]
    neighbor_relative_position: np.ndarray

    def __init__(
        self,
        type_name_substrings: List[str],
        relative_position: np.ndarray,
        relative_rotation: np.ndarray = None,
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
        relative_rotation: np.ndarray (optional)
            The relative rotation of this neighbor
            relative to the main particle
            Default: Calculate this from the neighbor_relative_positions
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
        self.relative_rotation = relative_rotation
        self.neighbor_type_name_substrings = neighbor_type_name_substrings
        self.neighbor_relative_position = neighbor_relative_position

    def _calculate_relative_rotation(self, other_neighbor_data: NeighborData):
        """
        Calculate relative rotation matrix for this neighbor
        from the main particle's rotation matrix
        if the neighbor's neighbor's position is given
        """
        if (
            self.neighbor_relative_position is None
            or self.relative_rotation is not None
        ):
            return
        # self = C, other = E
        particle_rotation = RotationUtility.get_rotation_from_neighbor_positions(
            other_neighbor_data.relative_position,
            self.relative_position,
        ) # E x C
        neighbor_rotation = RotationUtility.get_rotation_from_neighbor_positions(
            -1 * self.relative_position,
            self.neighbor_relative_position,
        ) # D
        if particle_rotation is None or neighbor_rotation is None:
            return
        self.relative_rotation = np.matmul(
            neighbor_rotation, np.linalg.inv(particle_rotation)
        )
