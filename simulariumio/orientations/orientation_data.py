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
        self.neighbor_data = neighbor_data

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
        Does the type_name contain all the type_name_substrings?

        Parameters
        ----------
        type_name: str
            Type name of the particle instance to match
        """
        return OrientationData._type_name_contains_substrings(
            self.type_name_substrings, type_name
        )

    def neighbor_type_name_matches(self, neighbor_number: int, type_name: str) -> bool:
        """
        Does the type_name contain all the neighbor's type_name_substrings?

        Parameters
        ----------
        neighbor_number : int
            Which neighbor to check, 0 or 1?
        type_name: str
            Type name of the particle instance to match
        """
        return OrientationData._type_name_contains_substrings(
            self.neighbor_data[neighbor_number].type_name_substrings, type_name
        )

    def get_neighbor_position(self, neighbor_number: int) -> np.ndarray:
        """
        Get the neighbor's relative_position

        Parameters
        ----------
        neighbor_number : int
            Which neighbor to check, 0 or 1?
        """
        return self.neighbor_data[neighbor_number].relative_position

    def get_neighbors_neighbor_position(self, neighbor_number: int) -> np.ndarray:
        """
        Get the neighbor's neighbor_relative_position

        Parameters
        ----------
        neighbor_number : int
            Which neighbor to check, 0 or 1?
        """
        return self.neighbor_data[neighbor_number].neighbor_relative_position
