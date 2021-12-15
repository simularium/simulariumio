#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

from .neighbor_data import NeighborData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class OrientationData:
    type_name_substrings: List[str]
    neighbor_data: List[NeighborData]

    def __init__(
        self,
        type_name_substrings: List[str],
        neighbor_data: List[NeighborData],
    ):
        """
        This object stores relative neighbor particle positions needed
        to calculate a particle's orientation.

        Note: whether a particle's neighbor is first or second is arbitrary,
        as long as it is kept consistent for a given type

        Parameters
        ----------
        type_name_substrings : List[str]
            The substrings that must be found
            in the type name of the particle being oriented
        neighbor_data: List[NeighborData]
            Type and position information for a neighbor
            of the particle being oriented
        """
        self.type_name_substrings = type_name_substrings
        if len(neighbor_data) > 2:
            print(
                f"OrientationData received {len(neighbor_data)} NeighborDatas, "
                "only the first 2 will be used"
            )
        self.neighbor_data = neighbor_data[:min(len(neighbor_data), 2)]
        self._calculate_neighbor_relative_rotation_matrices()

    def _calculate_neighbor_relative_rotation_matrices(self):
        """
        Calculate relative rotation matrix for each neighbor
        from the main particle's rotation matrix
        if the neighbor's neighbor's position is given
        """
        for index, neighbor_data in enumerate(self.neighbor_data):
            other_index = 1 - index
            neighbor_data._calculate_relative_rotation_matrix(self.neighbor_data[other_index])

    @staticmethod
    def _type_name_contains_substrings(substrings: List[str], type_name: str) -> bool:
        """
        Does the type_name contain all the substrings?
        """
        for substring in substrings:
            if substring not in type_name:
                return False
        return True

    def type_name_matches(self, type_name: str) -> bool:
        """
        Does the type_name contain all the type name substrings?

        Parameters
        ----------
        type_name: str
            Type name of the particle instance to match
        """
        return OrientationData._type_name_contains_substrings(
            self.type_name_substrings, type_name
        )

    def neighbor_type_name_matches(self, neighbor_index: int, type_name: str) -> bool:
        """
        Does the type_name contain all the neighbor's type name substrings?

        Parameters
        ----------
        neighbor_index : int
            Which neighbor to check, 0 or 1?
        type_name: str
            Type name of the particle instance to match
        """
        if len(self.neighbor_data) < neighbor_index + 1:
            return False
        return OrientationData._type_name_contains_substrings(
            self.neighbor_data[neighbor_index].type_name_substrings, type_name
        )

    def get_neighbor_position(self, neighbor_index: int) -> np.ndarray:
        """
        Get the neighbor's relative position

        Parameters
        ----------
        neighbor_index : int
            Which neighbor to check, 0 or 1?
        """
        if len(self.neighbor_data) < neighbor_index + 1:
            return False
        return self.neighbor_data[neighbor_index].relative_position

    def get_neighbors_neighbor_position(self, neighbor_index: int) -> np.ndarray:
        """
        Get the neighbor's neighbor relative position

        Parameters
        ----------
        neighbor_index : int
            Which neighbor to check, 0 or 1?
        """
        if len(self.neighbor_data) < neighbor_index + 1:
            return False
        return self.neighbor_data[neighbor_index].neighbor_relative_position

    def get_neighbor_relative_rotation_matrix(self, neighbor_index: int) -> np.ndarray:
        """
        Get the neighbor's relative rotation matrix

        Parameters
        ----------
        neighbor_index : int
            Which neighbor to check, 0 or 1?
        """
        if len(self.neighbor_data) < neighbor_index + 1:
            return False
        return self.neighbor_data[neighbor_index].relative_rotation_matrix
