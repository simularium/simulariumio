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
        if len(neighbor_data) < 2:
            raise Exception("OrientationData requires data for 2 neighbors")
        self.neighbor_data = neighbor_data[: min(len(neighbor_data), 2)]
        self._calculate_neighbor_relative_rotation_matrices()

    def _calculate_neighbor_relative_rotation_matrices(self):
        """
        Calculate relative rotation matrix for each neighbor
        from the main particle's rotation matrix
        if the neighbor's neighbor's position is given
        """
        for index, neighbor_data in enumerate(self.neighbor_data):
            other_index = 1 - index
            neighbor_data._calculate_relative_rotation_matrix(
                self.neighbor_data[other_index]
            )

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

    def _neighbor_index_is_invalid(self, neighbor_index) -> bool:
        """
        Check the given neighbor_index isn't too large
        for length of neighbor_data
        """
        return neighbor_index + 1 > len(self.neighbor_data) or neighbor_index < 0

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
        if self._neighbor_index_is_invalid(neighbor_index):
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
        if self._neighbor_index_is_invalid(neighbor_index):
            return None
        return self.neighbor_data[neighbor_index].relative_position

    def get_neighbor_relative_rotation_matrix(self, neighbor_index: int) -> np.ndarray:
        """
        Get the neighbor's relative rotation matrix

        Parameters
        ----------
        neighbor_index : int
            Which neighbor to check, 0 or 1?
        """
        if self._neighbor_index_is_invalid(neighbor_index):
            return None
        return self.neighbor_data[neighbor_index].relative_rotation_matrix

    def __str__(self):
        """
        Get a string representation of this object
        """
        neighbor1 = (
            str(self.neighbor_data[0]) if len(self.neighbor_data) > 0 else "None"
        )
        neighbor2 = (
            str(self.neighbor_data[1]) if len(self.neighbor_data) > 1 else "None"
        )
        return f"{self.type_name_substrings} :\n{neighbor1}\n{neighbor2}"
