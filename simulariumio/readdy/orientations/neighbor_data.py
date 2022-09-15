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
    relative_rotation_matrix: np.ndarray
    neighbor_type_name_substrings: List[str]
    neighbor_relative_position: np.ndarray

    def __init__(
        self,
        type_name_substrings: List[str],
        relative_position: np.ndarray,
        relative_rotation_matrix: np.ndarray = None,
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
        relative_position: np.ndarray (shape=3)
            The relative position
            of this neighbor of the particle being oriented
            in the space of the particle being oriented
        relative_rotation_matrix: np.ndarray (shape=(3,3)) (optional)
            The relative rotation of this neighbor
            relative to the main particle
            Default: Calculate this from the neighbor_relative_positions
        neighbor_type_name_substrings: List[str] (optional)
            The substrings that must be found in the type name
            of the neighbor of this neighbor of the particle being oriented
            Default: Don't calculate dependent particle orientations
                (e.g. particles with one neighbor at the end of a complex)
        neighbor_relative_position: np.ndarray (shape=3) (optional)
            The relative position of the neighbor B
            of this neighbor D of the particle being oriented C
            in the space of the particle being oriented C
            Default: Don't calculate dependent particle orientations
                (e.g. particles with one neighbor at the end of a complex)
        """
        self.type_name_substrings = type_name_substrings
        self.relative_position = relative_position
        self.relative_rotation_matrix = relative_rotation_matrix
        self.neighbor_type_name_substrings = neighbor_type_name_substrings
        self.neighbor_relative_position = neighbor_relative_position

    def _calculate_relative_rotation_matrix(self, other_neighbor_data: NeighborData):
        """
        Calculate relative rotation matrix for this neighbor
        from the main particle's rotation matrix
        if the neighbor's neighbor's position is given
        """
        # C relative to D
        if (
            self.neighbor_relative_position is None
            or self.relative_rotation_matrix is not None
        ):
            return
        particle_rotation_matrix = (  # D
            RotationUtility.get_rotation_matrix_from_neighbor_positions(
                self.relative_position,  # D -> C
                other_neighbor_data.relative_position,  # D -> E
            )
        )
        neighbor_rotation_matrix = (  # C
            RotationUtility.get_rotation_matrix_from_neighbor_positions(
                -1 * self.relative_position + self.neighbor_relative_position,  # C -> B
                -1 * self.relative_position,  # C -> D
            )
        )
        if particle_rotation_matrix is None or neighbor_rotation_matrix is None:
            return
        self.relative_rotation_matrix = np.matmul(
            neighbor_rotation_matrix, np.linalg.inv(particle_rotation_matrix)
        )

    def __str__(self):
        """
        Get a string representation of this object
        """
        return (
            f"neighbor = {self.type_name_substrings}, "
            f"neighbor neighbor = {self.neighbor_type_name_substrings}"
        )
